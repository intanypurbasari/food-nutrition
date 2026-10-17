"""Tests for src.evaluation.holdout."""

import numpy as np
import pandas as pd

from src.evaluation.holdout import HoldoutConfig, apply_masks, evaluate_source, make_masks, score, summarise
from src.imputation.baselines import mean_impute, median_impute


def _frame() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"food_id": [f"f{i}" for i in range(40)], "a": rng.normal(10, 2, 40), "b": rng.normal(5, 1, 40)})
    df.loc[:4, "b"] = np.nan
    return df


def test_masks_hide_only_observed_cells_and_respect_fraction():
    df = _frame()
    masks = make_masks(df, ["a", "b"], 0.15, np.random.default_rng(1), min_observed=10)
    assert len(masks["a"]) == 6  # 15% of 40
    assert len(masks["b"]) == 5  # 15% of 35 observed
    assert df.loc[masks["b"], "b"].notna().all()
    masked = apply_masks(df, masks)
    assert masked.loc[masks["a"], "a"].isna().all()
    assert df["a"].notna().all()  # original untouched


def test_columns_below_min_observed_are_skipped():
    df = _frame()
    df.loc[:35, "b"] = np.nan
    masks = make_masks(df, ["a", "b"], 0.15, np.random.default_rng(1), min_observed=10)
    assert "b" not in masks


def test_score_nrmse_is_one_for_mean_prediction():
    true = pd.Series([1.0, 2.0, 3.0, 4.0])
    result = score(true, pd.Series([true.mean()] * 4))
    assert abs(result["nrmse"] - 1.0) < 1e-9
    assert score(true, true)["rmse"] == 0.0


def test_evaluate_and_summarise_report_best_method():
    df = _frame()
    config = HoldoutConfig(fraction=0.15, repeats=2, seed=3)
    cells = evaluate_source("X", df, ["a", "b"], {"mean": mean_impute, "median": median_impute}, config, log=lambda _: None)
    assert set(cells["method"]) == {"mean", "median"}
    assert set(cells["repeat"]) == {1, 2}
    # the hidden true values are the original observed values
    lookup = df.set_index("food_id")
    assert all(lookup.at[f, n] == t for f, n, t in zip(cells["food_id"], cells["nutrient"], cells["true"]))
    summary = summarise(cells, {("X", "a"): 40, ("X", "b"): 35})
    assert summary.groupby("nutrient")["best_method"].nunique().eq(1).all()
    assert set(summary["n_holdout_cells"]) == {12, 10}  # 6 + 6 and 5 + 5 across two repeats
