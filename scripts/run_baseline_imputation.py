from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.imputation_settings import MYFCD_IMPUTED_BASELINE_PATHS, TKPI_IMPUTED_BASELINE_PATHS
from src.imputation import io_utils
from src.imputation.baselines import knn_impute, mean_impute, median_impute, mice_impute

ROOT = Path(__file__).resolve().parents[1]

METHODS = {"mean": mean_impute, "median": median_impute, "knn": knn_impute, "mice": mice_impute}

OUTPUT_PATHS = {"TKPI": TKPI_IMPUTED_BASELINE_PATHS, "MyFCD": MYFCD_IMPUTED_BASELINE_PATHS}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run baseline (mean/median/knn) imputation.")
    parser.add_argument("--method", choices=sorted(METHODS), default=None)
    args = parser.parse_args()

    methods_to_run = [args.method] if args.method else list(METHODS)

    target_columns = io_utils.columns_for_strategy("Imputasi internal per basis")
    print(f"[IMPUTE] baseline target columns ({len(target_columns)}): {target_columns}")

    for source in ["TKPI", "MyFCD"]:
        raw_df = io_utils.load_enriched(source)
        for method_name in methods_to_run:
            df = METHODS[method_name](raw_df, target_columns)
            print(f"[IMPUTE] {source}: applied {method_name}_impute")

            report = io_utils.validate_imputed_output(df, source, target_columns)
            remaining = sum(report["remaining_missing_in_targeted_columns"].values())
            print(f"[IMPUTE] {source}/{method_name}: remaining missing in targeted columns = {remaining}")

            io_utils.write_output(df, OUTPUT_PATHS[source][method_name])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
