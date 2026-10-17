"""Tests for src.evaluation.bootstrap."""

from pathlib import Path

import pandas as pd

from src.evaluation.bootstrap import BootstrapConfig, run_bootstrap, summarise_uncertainty

FIXTURES = Path(__file__).parent / "fixtures"
INTERNAL = ["water_g", "iron_mg", "calcium_mg", "phosphorus_mg", "potassium_mg"]


def _load(name: str) -> pd.DataFrame:
    return pd.read_csv(FIXTURES / name).drop(columns=["fixture_label"])


def test_bootstrap_covers_every_missing_cell_with_an_interval():
    tkpi = _load("sample_fixture_enriched_tkpi.csv")
    myfcd = _load("sample_fixture_enriched_myfcd.csv")
    cells = run_bootstrap(
        tkpi, myfcd, INTERNAL + ["carotene_total_mcg"], INTERNAL, ["carotene_total_mcg"],
        BootstrapConfig(n_boot=3, seed=1, n_jobs=1),
    )
    for source, frame, columns in [("TKPI", tkpi, INTERNAL + ["carotene_total_mcg"]), ("MyFCD", myfcd, INTERNAL + ["carotene_total_mcg"])]:
        expected = int(frame[columns].isna().sum().sum())
        assert (cells["source"] == source).sum() == expected
    assert set(cells.loc[cells["nutrient"] == "carotene_total_mcg", "method"]) <= {"crossdb", "missforest"}
    filled = cells[cells["n_boot"] > 0]
    assert (filled["ci_low"] <= filled["ci_high"]).all()

    observed_sd = pd.Series({(s, n): 1.0 for s, n in zip(cells["source"], cells["nutrient"])})
    summary = summarise_uncertainty(cells, observed_sd, threshold=0.5)
    assert {"high_uncertainty", "median_relative_sd"} <= set(summary.columns)
