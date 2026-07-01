from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.settings import MYFCD_URL, TKPI_URL
from src.scrapers.base import ROOT, fetch_with_cache, looks_js_heavy, setup_logger


def inspect_source(name: str, url: str) -> dict:
    logger = setup_logger("source_recon", ROOT / "logs" / "source_recon.log")
    html, meta = fetch_with_cache(url, "source_recon", logger)
    if html is None:
        return {
            "source": name,
            "url": url,
            "status": "blocked",
            "notes": f"Request failed or returned an error status: {meta}",
            "selector_candidates": [],
        }

    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    forms = soup.find_all("form")
    links = soup.find_all("a")
    candidate_selectors = []
    if tables:
        candidate_selectors.append("table")
    if forms:
        candidate_selectors.append("form")
    if soup.select(".pagination"):
        candidate_selectors.append(".pagination")
    if soup.select(".card"):
        candidate_selectors.append(".card")
    if soup.select(".list-group-item"):
        candidate_selectors.append(".list-group-item")

    protection_markers = ["captcha", "forbidden", "access denied", "too many requests"]
    lower_html = html.lower()
    protected = any(marker in lower_html for marker in protection_markers)
    js_required = looks_js_heavy(html)
    public_flow_detected = (name == "TKPI" and bool(forms)) or (
        name == "MyFCD" and "index.php/ajax/datatable_data" in html
    )
    status = "accessible"
    notes = []
    if protected:
        status = "blocked"
        notes.append("HTML contains possible captcha/access protection markers.")
    elif public_flow_detected:
        status = "accessible"
        notes.append("A normal public form/AJAX flow for limited extraction was detected.")
    elif js_required:
        status = "JS-required"
        notes.append("Initial HTML appears JavaScript-heavy or lacks static data selectors.")
    else:
        notes.append("Initial HTML was fetched with requests and contains inspectable markup.")

    notes.append(f"tables={len(tables)}, forms={len(forms)}, links={len(links)}")
    if name == "TKPI" and forms:
        notes.append("Normal category POST flow is available for limited listing/detail extraction.")
    if name == "MyFCD" and "index.php/ajax/datatable_data" in html:
        notes.append("Public DataTables AJAX endpoint is referenced by the page.")

    return {
        "source": name,
        "url": url,
        "status": status,
        "notes": " ".join(notes),
        "selector_candidates": candidate_selectors,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def write_reports(results: list[dict]) -> None:
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "reports").mkdir(exist_ok=True)
    summary_path = ROOT / "reports" / "source_recon_summary.json"
    summary_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# Source Reconnaissance Report", ""]
    lines.append("Recon dilakukan ringan dengan request terbatas, delay minimal, cache lokal, dan tanpa bypass proteksi.")
    lines.append("")
    for item in results:
        lines.extend(
            [
                f"## {item['source']}",
                "",
                f"- URL: {item['url']}",
                f"- Status: {item['status']}",
                f"- Selector kandidat: {', '.join(item['selector_candidates']) or '-'}",
                f"- Catatan: {item['notes']}",
                "",
            ]
        )
    (ROOT / "docs" / "source_recon_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    results = [inspect_source("TKPI", TKPI_URL), inspect_source("MyFCD", MYFCD_URL)]
    write_reports(results)
    for result in results:
        print(f"[RECON] {result['source']}: {result['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
