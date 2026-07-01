import math
import re
import unicodedata
from typing import Any

from src.schema.nutrition_schema import NUTRIENT_FIELDS


MISSING_TOKENS = {"", "-", "--", "na", "n/a", "nan", "none", "null", "tidak ada", "tr", "trace"}


def is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return str(value).strip().lower() in MISSING_TOKENS


def normalize_numeric(value: Any) -> float | None:
    if is_missing(value):
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)

    text = str(value).strip().lower()
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[^\d,.\-+]", "", text)
    if text in {"", "-", "+", ".", ","}:
        return None

    if "," in text and "." in text:
        text = text.replace(",", "")
    elif "," in text:
        text = text.replace(",", ".")

    try:
        return float(text)
    except ValueError:
        return None


def normalize_column_name(name: Any) -> str:
    text = unicodedata.normalize("NFKD", str(name or ""))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.strip().lower()
    text = re.sub(r"[%/()]+", " ", text)
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def normalize_food_name(name: Any) -> str:
    text = unicodedata.normalize("NFKC", str(name or ""))
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s\-/().,]", "", text, flags=re.UNICODE)
    return text.strip()


def normalize_category(name: Any) -> str | None:
    if is_missing(name):
        return None
    text = normalize_food_name(name)
    text = re.sub(r"\s+", " ", text)
    return text or None


def compute_missing_nutrient_count(record_dict: dict[str, Any]) -> int:
    return sum(1 for field in NUTRIENT_FIELDS if is_missing(record_dict.get(field)))


def compute_completeness_score(record_dict: dict[str, Any]) -> float:
    if not NUTRIENT_FIELDS:
        return 0.0
    present = len(NUTRIENT_FIELDS) - compute_missing_nutrient_count(record_dict)
    return round(present / len(NUTRIENT_FIELDS), 4)
