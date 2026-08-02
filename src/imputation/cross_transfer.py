"""Cross-database MissForest transfer: fit on TKPI, apply to MyFCD.

This is the project's stated methodological novelty (README: "MissForest
dengan pendekatan cross-database transfer, imputer dilatih pada TKPI,
diterapkan pada MyFCD"). For nutrients where MyFCD has 0% availability but
TKPI has partial real data (availability_matrix.csv's
"Cross-DB transfer / USDA" strategy, e.g. carotene_total_mcg), an imputer is
fit on TKPI's fuller distribution and its fitted per-feature relationships
are applied to fill those columns in MyFCD - which lacks the signal to
impute them from its own data at all.

Reuses src.imputation.missforest_imputer.fit_random_forest_imputer (the same
underlying random-forest-imputation implementation as the within-database
method in Milestone 6) rather than a second, parallel implementation. Only
the train/apply split differs: within-database fits and transforms the same
frame; this module fits on train_df and transforms a different apply_df.
"""

from __future__ import annotations

import pandas as pd

from config.imputation_settings import RANDOM_SEED
from src.cleaning.normalizers import is_missing
from src.imputation.missforest_imputer import fit_random_forest_imputer


def _to_numeric_with_missing(series: pd.Series) -> pd.Series:
    return series.apply(lambda value: None if is_missing(value) else value).astype(float)


def cross_db_transfer_impute(
    train_df: pd.DataFrame, apply_df: pd.DataFrame, columns: list[str], random_state: int | None = None
) -> pd.DataFrame:
    """Fit a MissForest-style imputer on `train_df` (TKPI) and apply it to `apply_df` (MyFCD).

    `train_df` is purely the training source and is never modified or
    returned - it is used only to fit the per-feature random-forest
    estimators over the shared NUTRIENT_FIELDS space. Those fitted
    estimators are then applied to `apply_df` to fill `columns`. Returns a
    copy of `apply_df` with only `columns` replaced; every other column in
    `apply_df` is unchanged.
    """
    if random_state is None:
        random_state = RANDOM_SEED

    imputer = fit_random_forest_imputer(train_df, random_state=random_state)
    predictor_columns = imputer.feature_names_in_stage3_

    apply_numeric_block = pd.DataFrame(
        {column: _to_numeric_with_missing(apply_df[column]) for column in predictor_columns if column in apply_df.columns}
    )
    # Predictor columns fit on train_df but absent from apply_df's own
    # schema cannot occur in this pipeline (TKPI/MyFCD share the same
    # NUTRIENT_FIELDS schema), but guard defensively rather than assume.
    missing_in_apply = [column for column in predictor_columns if column not in apply_df.columns]
    if missing_in_apply:
        raise ValueError(f"apply_df is missing predictor columns fit on train_df: {missing_in_apply}")

    imputed_values = imputer.transform(apply_numeric_block)
    imputed_df = pd.DataFrame(imputed_values, columns=predictor_columns, index=apply_df.index)

    result = apply_df.copy()
    target_columns = [column for column in columns if column in predictor_columns]
    result[target_columns] = imputed_df[target_columns]
    return result
