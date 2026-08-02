"""Stage 3 (ML imputation) configuration: paths, nutrient groupings, and run parameters."""

from pathlib import Path

from src.schema.nutrition_schema import NUTRIENT_FIELDS

ROOT = Path(__file__).resolve().parents[1]

RANDOM_SEED = 42

# --- Inputs (Stage 1 / Stage 2 outputs, read-only) ---
TKPI_ENRICHED_PATH = ROOT / "data_processed" / "tkpi_enriched.csv"
MYFCD_ENRICHED_PATH = ROOT / "data_processed" / "myfcd_enriched.csv"
AVAILABILITY_MATRIX_PATH = ROOT / "data_processed" / "availability_matrix.csv"
TKPI_MYFCD_LINKS_MUTUAL_PATH = ROOT / "data_processed" / "tkpi_myfcd_links_mutual.csv"
NUTRITION_REPOSITORY_SAMPLE_PATH = ROOT / "data_processed" / "nutrition_repository_sample.csv"

# --- Baseline imputation outputs (Milestones 3-5) ---
# Per-method suffixed paths (mean/median/knn/mice each write their own file,
# so Milestone 9's evaluation export can compare methods independently).
# Supersedes the Milestone 3 single shared filename below.
BASELINE_METHODS = ["mean", "median", "knn", "mice"]
TKPI_IMPUTED_BASELINE_PATHS = {
    method: ROOT / "data_processed" / f"tkpi_imputed_baseline_{method}.csv" for method in BASELINE_METHODS
}
MYFCD_IMPUTED_BASELINE_PATHS = {
    method: ROOT / "data_processed" / f"myfcd_imputed_baseline_{method}.csv" for method in BASELINE_METHODS
}

# --- MissForest outputs (Milestones 6-7) ---
TKPI_IMPUTED_MISSFOREST_PATH = ROOT / "data_processed" / "tkpi_imputed_missforest.csv"
MYFCD_IMPUTED_MISSFOREST_PATH = ROOT / "data_processed" / "myfcd_imputed_missforest.csv"
MYFCD_IMPUTED_CROSSDB_PATH = ROOT / "data_processed" / "myfcd_imputed_crossdb.csv"

# --- Integrated / evaluation outputs (Milestones 8-9) ---
NUTRITION_REPOSITORY_IMPUTED_PATH = ROOT / "data_processed" / "nutrition_repository_imputed.csv"
NUTRITION_REPOSITORY_IMPUTED_LONG_PATH = ROOT / "data_processed" / "nutrition_repository_imputed_long.csv"

# --- Reports ---
IMPUTATION_SUMMARY_REPORT_PATH = ROOT / "reports" / "imputation_summary.md"
IMPUTATION_METHOD_COMPARISON_REPORT_PATH = ROOT / "reports" / "imputation_method_comparison.csv"

# Nutrient groupings mirror src.schema.nutrition_schema.NUTRIENT_FIELDS exactly;
# imported (not copy/pasted) so the two lists cannot diverge.
IMPUTATION_NUTRIENT_FIELDS = list(NUTRIENT_FIELDS)

# USDA value-borrowed columns already present in *_enriched.csv (Stage 1 output).
# Stage 3 consumes these as-is; it does not redo value borrowing.
USDA_BORROWED_COLUMNS = [
    "magnesium_mg",
    "sugars_total_g",
    "saturated_fat_g",
    "cholesterol_mg",
    "vitamin_b6_mg",
    "vitamin_b12_mcg",
]
