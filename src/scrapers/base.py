from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

from config.settings import REQUEST_DELAY_SECONDS, REQUEST_TIMEOUT_SECONDS, USER_AGENT


ROOT = Path(__file__).resolve().parents[2]


@dataclass
class ScrapeResult:
    rows: list[dict[str, Any]]
    errors: list[dict[str, Any]]


def ensure_runtime_dirs() -> None:
    for folder in ["data_raw", "reports", "logs", "cache"]:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)


def setup_logger(name: str, log_file: Path) -> logging.Logger:
    ensure_runtime_dirs()
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


def _cache_path(url: str, cache_namespace: str, payload: Any = None) -> Path:
    key = url if payload is None else f"{url}|{json.dumps(payload, sort_keys=True, ensure_ascii=False)}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    cache_dir = ROOT / "cache" / cache_namespace
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{digest}.html"


def fetch_with_cache(url: str, cache_namespace: str, logger: logging.Logger) -> tuple[str | None, dict[str, Any]]:
    ensure_runtime_dirs()
    cache_path = _cache_path(url, cache_namespace)

    if cache_path.exists():
        logger.info("cache_hit url=%s path=%s", url, cache_path)
        return cache_path.read_text(encoding="utf-8", errors="replace"), {
            "url": url,
            "status_code": "cache",
            "cached": True,
        }

    time.sleep(max(REQUEST_DELAY_SECONDS, 2))
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        logger.info("request url=%s status=%s", url, response.status_code)
        if response.status_code >= 400:
            return None, {"url": url, "status_code": response.status_code, "cached": False}
        cache_path.write_text(response.text, encoding="utf-8")
        return response.text, {"url": url, "status_code": response.status_code, "cached": False}
    except requests.RequestException as exc:
        logger.error("request_failed url=%s error=%s", url, exc)
        return None, {"url": url, "status_code": "request_error", "error": str(exc), "cached": False}


def post_with_cache(
    url: str,
    data: Any,
    cache_namespace: str,
    logger: logging.Logger,
    extra_headers: dict[str, str] | None = None,
) -> tuple[str | None, dict[str, Any]]:
    ensure_runtime_dirs()
    cache_path = _cache_path(url, cache_namespace, payload=data)

    if cache_path.exists():
        logger.info("cache_hit method=post url=%s path=%s", url, cache_path)
        return cache_path.read_text(encoding="utf-8", errors="replace"), {
            "url": url,
            "status_code": "cache",
            "cached": True,
        }

    headers = {"User-Agent": USER_AGENT}
    if extra_headers:
        headers.update(extra_headers)
    last_error = None
    for attempt in range(1, 4):
        time.sleep(max(REQUEST_DELAY_SECONDS, 2) * attempt)
        try:
            response = requests.post(url, headers=headers, data=data, timeout=REQUEST_TIMEOUT_SECONDS)
            logger.info("post url=%s status=%s attempt=%s", url, response.status_code, attempt)
            if response.status_code >= 500 and attempt < 3:
                last_error = f"server_status_{response.status_code}"
                continue
            if response.status_code >= 400:
                return None, {"url": url, "status_code": response.status_code, "cached": False}
            cache_path.write_text(response.text, encoding="utf-8")
            return response.text, {"url": url, "status_code": response.status_code, "cached": False}
        except requests.RequestException as exc:
            last_error = str(exc)
            logger.warning("post_failed url=%s attempt=%s error=%s", url, attempt, exc)
            if attempt == 3:
                logger.error("post_failed_final url=%s error=%s", url, exc)
    return None, {"url": url, "status_code": "request_error", "error": last_error, "cached": False}


def table_rows_from_html(html: str, source_url: str, source: str, limit: int) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, Any]] = []
    food_header_terms = {"food", "nama", "bahan", "makanan"}

    for table in soup.find_all("table"):
        headers = [cell.get_text(" ", strip=True) for cell in table.find_all("th")]
        body_rows = table.find_all("tr")
        if not headers and body_rows:
            first_cells = body_rows[0].find_all(["td", "th"])
            headers = [cell.get_text(" ", strip=True) for cell in first_cells]
            body_rows = body_rows[1:]
        if not headers:
            continue
        normalized_headers = {header.lower() for header in headers}
        if not any(any(term in header for term in food_header_terms) for header in normalized_headers):
            continue

        for tr in body_rows:
            cells = [cell.get_text(" ", strip=True) for cell in tr.find_all("td")]
            if not cells:
                continue
            record = {headers[i] if i < len(headers) else f"column_{i+1}": value for i, value in enumerate(cells)}
            record.update({"source": source, "source_url": source_url, "scraped_at": scraped_at})
            rows.append(record)
            if len(rows) >= limit:
                return rows
    return rows


def generic_candidate_rows_from_html(html: str, source_url: str, source: str, limit: int) -> list[dict[str, Any]]:
    """Inspect generic lists without treating them as final food data.

    This helper is intentionally unused by production scraper entry points because
    arbitrary navigation/list text can look like rows but is not trustworthy enough
    for raw nutrition output.
    """
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, Any]] = []
    selectors = [".card", ".list-group-item", "li", "article"]

    for selector in selectors:
        for element in soup.select(selector):
            text = element.get_text(" ", strip=True)
            if len(text) < 3:
                continue
            rows.append(
                {
                    "food_name_original": text[:250],
                    "source": source,
                    "source_url": source_url,
                    "scraped_at": scraped_at,
                    "raw_text": text,
                }
            )
            if len(rows) >= limit:
                return rows
        if rows:
            return rows
    return rows


def write_raw_outputs(rows: list[dict[str, Any]], source_slug: str, columns: list[str] | None = None) -> None:
    ensure_runtime_dirs()
    csv_path = ROOT / "data_raw" / f"{source_slug}_raw.csv"
    json_path = ROOT / "data_raw" / f"{source_slug}_raw.json"
    df = pd.DataFrame(rows)
    if columns:
        remaining_columns = [column for column in df.columns if column not in columns]
        for column in columns:
            if column not in df.columns:
                df[column] = None
        df = df[columns + remaining_columns]
    df.to_csv(csv_path, index=False, encoding="utf-8")
    records = json.loads(df.where(pd.notna(df), None).to_json(orient="records", force_ascii=False))
    json_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def write_json_report(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def looks_js_heavy(html: str) -> bool:
    soup = BeautifulSoup(html, "html.parser")
    visible_text = soup.get_text(" ", strip=True)
    script_count = len(soup.find_all("script"))
    table_count = len(soup.find_all("table"))
    form_count = len(soup.find_all("form"))
    app_markers = ["__next", "ng-app", "react", "vue", "app-root"]
    marker_found = any(marker in html.lower() for marker in app_markers)
    return (script_count >= 5 and table_count == 0 and len(visible_text) < 1000) or (marker_found and form_count == 0)


def source_slug_from_url(url: str) -> str:
    host = urlparse(url).netloc.replace(".", "_")
    return host or "source"
