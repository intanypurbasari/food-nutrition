"""Within-database MissForest-style imputation.

`missingpy` (the original MissForest package) was evaluated in Milestone 1
and found unmaintained/broken against current scikit-learn (it imports the
long-removed `sklearn.neighbors.base` module). Stage 3 instead uses
scikit-learn's own `IterativeImputer(estimator=RandomForestRegressor)`,
which implements the same missForest algorithm (iterative, per-feature
random-forest regression against the other features) without that
dependency.

This module fits and applies the imputer within a single source only - it
must never mix TKPI and MyFCD rows. See src.imputation.cross_transfer for
the cross-database (train-on-TKPI, apply-to-MyFCD) variant, which reuses
`fit_random_forest_imputer` from this module rather than duplicating the
random-forest-imputation implementation.
"""

from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.experimental import enable_iterative_imputer  # noqa: F401  (required by IterativeImputer)
from sklearn.impute import IterativeImputer

from config.imputation_settings import IMPUTATION_NUTRIENT_FIELDS, RANDOM_SEED
from src.cleaning.normalizers import is_missing

MISSFOREST_MAX_ITER = 10
MISSFOREST_N_ESTIMATORS = 50


def _to_numeric_with_missing(series: pd.Series) -> pd.Series:
    """Coerce a column to numeric, treating repo-canonical missing tokens as NaN."""
    return series.apply(lambda value: None if is_missing(value) else value).astype(float)


def _predictor_columns(df: pd.DataFrame) -> list[str]:
    """The shared nutrient feature space usable as IterativeImputer input for `df`.

    Using the full feature space - not just the target `columns` - is what
    gives MissForest its multivariate signal from correlated nutrients,
    unlike the univariate mean/median baselines. Columns with zero observed
    values in `df` (e.g. vitamin_a_mcg, 100% missing in both sources) are
    excluded: scikit-learn's IterativeImputer silently drops such columns
    from its output entirely, which would
    otherwise misalign the result against the requested column list.
    """
    candidate_columns = [field for field in IMPUTATION_NUTRIENT_FIELDS if field in df.columns]
    return [column for column in candidate_columns if not df[column].apply(is_missing).all()]


def fit_random_forest_imputer(train_frame: pd.DataFrame, random_state: int | None = None) -> IterativeImputer:
    """Fit an IterativeImputer(RandomForestRegressor) on `train_frame`'s nutrient columns.

    Shared low-level fit step reused by both missforest_impute (within-
    database, fit and transform on the same source) and
    src.imputation.cross_transfer.cross_db_transfer_impute (fit on TKPI,
    transform MyFCD).
    """
    if random_state is None:
        random_state = RANDOM_SEED

    predictor_columns = _predictor_columns(train_frame)
    numeric_block = pd.DataFrame(
        {column: _to_numeric_with_missing(train_frame[column]) for column in predictor_columns}
    )
    imputer = IterativeImputer(
        estimator=RandomForestRegressor(n_estimators=MISSFOREST_N_ESTIMATORS, random_state=random_state),
        max_iter=MISSFOREST_MAX_ITER,
        random_state=random_state,
    )
    imputer.fit(numeric_block)
    imputer.feature_names_in_stage3_ = predictor_columns  # remember fit column order for transform()
    return imputer


def missforest_impute(df: pd.DataFrame, columns: list[str], random_state: int | None = None) -> pd.DataFrame:
    """Within-source MissForest-style imputation, restricted to `columns` in the output.

    Fits on df's own full nutrient feature space (for multivariate signal)
    and transforms the same df, but only `columns` are written back into the
    result - every other column, including predictor-only columns not in
    `columns`, passes through unchanged. Must be called once per source; do
    not mix TKPI and MyFCD rows in a single call.
    """
    if random_state is None:
        random_state = RANDOM_SEED

    result = df.copy()
    imputer = fit_random_forest_imputer(df, random_state=random_state)
    predictor_columns = imputer.feature_names_in_stage3_
    numeric_block = pd.DataFrame(
        {column: _to_numeric_with_missing(df[column]) for column in predictor_columns}
    )
    imputed_values = imputer.transform(numeric_block)
    imputed_df = pd.DataFrame(imputed_values, columns=predictor_columns, index=df.index)

    target_columns = [column for column in columns if column in predictor_columns]
    result[target_columns] = imputed_df[target_columns]
    return result
