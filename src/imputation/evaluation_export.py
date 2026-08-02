"""Long-format, evaluation-ready export combining every Stage 3 method's output.

This module reshapes data for Stage 4 (evaluation, a different team member's
responsibility) to consume. It does NOT compute any accuracy/error metric
against ground truth - that comparison against held-out real values is
explicitly Stage 4's job, not Stage 3's.
"""

from __future__ import annotations

import pandas as pd

ID_COLUMNS = ["food_id", "source"]
LONG_FORMAT_COLUMNS = ["food_id", "source_db", "nutrient", "method", "value"]


def to_long_format(sources: dict[str, pd.DataFrame], value_columns: list[str]) -> pd.DataFrame:
    """Melt each method's DataFrame into long format and concatenate all methods.

    `sources` is a dict keyed by method name (e.g. "mean", "median", "knn",
    "mice", "missforest", "crossdb", "original"), each DataFrame including
    food_id and source columns plus whichever of `value_columns` it has.
    Output columns: food_id, source_db, nutrient, method, value. Rows where
    value is still NaN are kept (not dropped) - Stage 4 needs to see
    unresolved cells (e.g. vitamin_a_mcg) too.
    """
    frames = []
    for method, df in sources.items():
        present_value_columns = [column for column in value_columns if column in df.columns]
        melted = df[ID_COLUMNS + present_value_columns].melt(
            id_vars=ID_COLUMNS, value_vars=present_value_columns, var_name="nutrient", value_name="value"
        )
        melted = melted.rename(columns={"source": "source_db"})
        melted["method"] = method
        frames.append(melted[LONG_FORMAT_COLUMNS])

    if not frames:
        return pd.DataFrame(columns=LONG_FORMAT_COLUMNS)
    return pd.concat(frames, ignore_index=True)


def compute_method_comparison(long_df: pd.DataFrame) -> pd.DataFrame:
    """Descriptive statistics (count/mean/std) per (nutrient, method) pair.

    This is explicitly descriptive only - NOT an accuracy/error metric
    against ground truth, which is Stage 4's responsibility.
    """
    grouped = long_df.groupby(["nutrient", "method"], as_index=False)["value"].agg(
        count="count", mean="mean", std="std"
    )
    return grouped.sort_values(["nutrient", "method"]).reset_index(drop=True)
