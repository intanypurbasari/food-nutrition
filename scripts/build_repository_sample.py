from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.schema.nutrition_schema import schema_columns


ROOT = Path(__file__).resolve().parents[1]


def load_clean(source: str, path: Path) -> pd.DataFrame | None:
    if not path.exists() or path.stat().st_size == 0:
        print(f"[MERGE] {source}: skipped, clean file not found")
        return None
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        print(f"[MERGE] {source}: skipped, clean file empty")
        return None
    if df.empty:
        print(f"[MERGE] {source}: skipped, no rows")
        return None
    df["source"] = source
    return df


def flag_potential_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "food_name_normalized" not in df.columns:
        return df
    counts = Counter(name for name in df["food_name_normalized"].fillna("") if name)
    duplicate_names = {name for name, count in counts.items() if count > 1}
    if not duplicate_names:
        return df

    def add_note(row: pd.Series) -> str:
        note = "" if pd.isna(row.get("notes")) else str(row.get("notes"))
        if row.get("food_name_normalized") in duplicate_names:
            extra = "potential duplicate name across repository; review manually"
            return f"{note}; {extra}".strip("; ")
        return note

    df["notes"] = df.apply(add_note, axis=1)
    return df


def regenerate_ids(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    counters: dict[str, int] = {}
    ids = []
    for source in df["source"].fillna("unknown"):
        prefix = "tkpi" if source == "TKPI" else "myfcd" if source == "MyFCD" else str(source).lower()
        counters[prefix] = counters.get(prefix, 0) + 1
        ids.append(f"{prefix}_{counters[prefix]:04d}")
    df["food_id"] = ids
    return df


def main() -> int:
    frames = []
    for source, path in [
        ("TKPI", ROOT / "data_clean" / "tkpi_clean.csv"),
        ("MyFCD", ROOT / "data_clean" / "myfcd_clean.csv"),
    ]:
        df = load_clean(source, path)
        if df is not None:
            frames.append(df)

    (ROOT / "data_processed").mkdir(exist_ok=True)
    (ROOT / "reports").mkdir(exist_ok=True)

    if frames:
        merged = pd.concat(frames, ignore_index=True)
        for column in schema_columns():
            if column not in merged.columns:
                merged[column] = None
        merged = merged[schema_columns()]
        merged = regenerate_ids(flag_potential_duplicates(merged))
    else:
        merged = pd.DataFrame(columns=schema_columns())

    output_path = ROOT / "data_processed" / "nutrition_repository_sample.csv"
    merged.to_csv(output_path, index=False, encoding="utf-8")

    counts = merged["source"].value_counts().to_dict() if not merged.empty else {}
    duplicate_count = int(merged.duplicated(subset=["food_name_normalized"], keep=False).sum()) if not merged.empty else 0
    lines = [
        "# Integration Summary",
        "",
        f"- Total rows: {len(merged)}",
        f"- TKPI rows: {counts.get('TKPI', 0)}",
        f"- MyFCD rows: {counts.get('MyFCD', 0)}",
        f"- Potential duplicate food-name rows flagged: {duplicate_count}",
        "",
        "Entity matching lintas sumber tidak dilakukan otomatis pada tahap ini. Nama makanan yang tampak mirip hanya diberi catatan untuk review manual/future work.",
    ]
    (ROOT / "reports" / "integration_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[MERGE] repository rows written: {len(merged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
