from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.imputation_settings import MYFCD_IMPUTED_MISSFOREST_PATH, TKPI_IMPUTED_MISSFOREST_PATH
from src.imputation import io_utils
from src.imputation.missforest_imputer import missforest_impute

ROOT = Path(__file__).resolve().parents[1]

OUTPUT_PATHS = {"TKPI": TKPI_IMPUTED_MISSFOREST_PATH, "MyFCD": MYFCD_IMPUTED_MISSFOREST_PATH}


def run_within_database() -> None:
    target_columns = io_utils.columns_for_strategy("Imputasi internal per basis")
    print(f"[IMPUTE] missforest (within-database) target columns ({len(target_columns)}): {target_columns}")

    for source in ["TKPI", "MyFCD"]:
        df = io_utils.load_enriched(source)
        imputed = missforest_impute(df, target_columns)
        print(f"[IMPUTE] {source}: applied missforest_impute")

        report = io_utils.validate_imputed_output(imputed, source, target_columns)
        remaining = sum(report["remaining_missing_in_targeted_columns"].values())
        print(f"[IMPUTE] {source}/missforest: remaining missing in targeted columns = {remaining}")

        io_utils.write_output(imputed, OUTPUT_PATHS[source])


def main() -> int:
    run_within_database()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
