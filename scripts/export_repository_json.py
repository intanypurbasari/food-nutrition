from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


ROOT = Path(__file__).resolve().parents[1]


def df_records(df: pd.DataFrame) -> list[dict]:
    clean_df = df.where(pd.notna(df), None)
    return json.loads(clean_df.to_json(orient="records", force_ascii=False))


def main() -> int:
    input_path = ROOT / "data_processed" / "nutrition_repository_imputed.csv"
    if not input_path.exists() or input_path.stat().st_size == 0:
        print("Repository CSV not found. Run scripts/run_integration.py first.")
        return 1

    try:
        df = pd.read_csv(input_path)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame()

    records = df_records(df)
    out_dir = ROOT / "data_processed"
    out_dir.mkdir(exist_ok=True)

    by_source = {"TKPI": [], "MyFCD": []}
    for source, group in df.groupby("source") if "source" in df.columns else []:
        by_source[str(source)] = df_records(group)
    (out_dir / "nutrition_repository_by_source.json").write_text(
        json.dumps(by_source, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    by_category = {}
    if "category_normalized" in df.columns:
        for category, group in df.groupby(df["category_normalized"].fillna("uncategorized")):
            by_category[str(category)] = df_records(group)
    (out_dir / "nutrition_repository_by_category.json").write_text(
        json.dumps(by_category, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"[EXPORT] JSON files written from {len(records)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
