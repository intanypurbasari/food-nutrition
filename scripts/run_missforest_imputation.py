from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.imputation_settings import (
    MYFCD_IMPUTED_CROSSDB_PATH,
    MYFCD_IMPUTED_MISSFOREST_PATH,
    TKPI_IMPUTED_MISSFOREST_PATH,
)
from src.imputation import io_utils
from src.imputation.cross_transfer import cross_db_transfer_impute
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


def run_cross_database_transfer() -> None:
    target_columns = io_utils.columns_for_strategy("Cross-DB transfer / USDA")
    print(f"[IMPUTE] missforest (cross-DB transfer, TKPI->MyFCD) target columns: {target_columns}")

    train_df = io_utils.load_enriched("TKPI")
    apply_df = io_utils.load_enriched("MyFCD")
    train_df_before = train_df.copy()

    imputed_myfcd = cross_db_transfer_impute(train_df=train_df, apply_df=apply_df, columns=target_columns)
    print("[IMPUTE] MyFCD: applied cross_db_transfer_impute (trained on TKPI)")

    assert train_df.equals(train_df_before), "cross_db_transfer_impute must not mutate train_df (TKPI)"

    report = io_utils.validate_imputed_output(imputed_myfcd, "MyFCD", target_columns)
    remaining = sum(report["remaining_missing_in_targeted_columns"].values())
    print(f"[IMPUTE] MyFCD/crossdb: remaining missing in targeted columns = {remaining}")

    io_utils.write_output(imputed_myfcd, MYFCD_IMPUTED_CROSSDB_PATH)


def main() -> int:
    run_within_database()
    run_cross_database_transfer()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
