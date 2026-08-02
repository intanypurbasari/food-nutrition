from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.imputation_settings import (
    IMPUTATION_METHOD_COMPARISON_REPORT_PATH,
    IMPUTATION_NUTRIENT_FIELDS,
    MYFCD_IMPUTED_BASELINE_PATHS,
    MYFCD_IMPUTED_CROSSDB_PATH,
    MYFCD_IMPUTED_MISSFOREST_PATH,
    NUTRITION_REPOSITORY_IMPUTED_LONG_PATH,
    NUTRITION_REPOSITORY_SAMPLE_PATH,
    TKPI_IMPUTED_BASELINE_PATHS,
    TKPI_IMPUTED_MISSFOREST_PATH,
)
from src.imputation import io_utils
from src.imputation.evaluation_export import compute_method_comparison, to_long_format

ROOT = Path(__file__).resolve().parents[1]

COMPARISON_REPORT_HEADER = (
    "# Descriptive statistics only (count/mean/std of imputed values per nutrient x method). "
    "This is NOT an accuracy/error metric against ground truth - that comparison against "
    "held-out real values is Stage 4's responsibility, not this script's.\n"
)


def _load_required_csv(label: str, path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        raise FileNotFoundError(
            f"Required Stage 3 output '{label}' not found at {path}. "
            "Run the corresponding milestone's script first."
        )
    df = pd.read_csv(path)
    print(f"[IMPUTE] loaded {label}: {len(df)} rows from {path.name}")
    return df


def build_sources() -> dict[str, pd.DataFrame]:
    sources: dict[str, pd.DataFrame] = {}

    for method in TKPI_IMPUTED_BASELINE_PATHS:
        tkpi_df = _load_required_csv(f"tkpi_baseline_{method}", TKPI_IMPUTED_BASELINE_PATHS[method])
        myfcd_df = _load_required_csv(f"myfcd_baseline_{method}", MYFCD_IMPUTED_BASELINE_PATHS[method])
        sources[method] = pd.concat([tkpi_df, myfcd_df], ignore_index=True)

    tkpi_missforest = _load_required_csv("tkpi_missforest", TKPI_IMPUTED_MISSFOREST_PATH)
    myfcd_missforest = _load_required_csv("myfcd_missforest", MYFCD_IMPUTED_MISSFOREST_PATH)
    sources["missforest"] = pd.concat([tkpi_missforest, myfcd_missforest], ignore_index=True)

    sources["crossdb"] = _load_required_csv("myfcd_crossdb", MYFCD_IMPUTED_CROSSDB_PATH)

    sources["original"] = _load_required_csv("nutrition_repository_sample", NUTRITION_REPOSITORY_SAMPLE_PATH)

    return sources


def main() -> int:
    sources = build_sources()

    long_df = to_long_format(sources, IMPUTATION_NUTRIENT_FIELDS)
    io_utils.write_output(long_df, NUTRITION_REPOSITORY_IMPUTED_LONG_PATH)

    comparison = compute_method_comparison(long_df)
    IMPUTATION_METHOD_COMPARISON_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with IMPUTATION_METHOD_COMPARISON_REPORT_PATH.open("w", encoding="utf-8") as handle:
        handle.write(COMPARISON_REPORT_HEADER)
        comparison.to_csv(handle, index=False)
    print(f"[IMPUTE] wrote {IMPUTATION_METHOD_COMPARISON_REPORT_PATH}")

    print(f"[IMPUTE] long-format rows: {len(long_df)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
