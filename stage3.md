# Stage 3 (Machine Learning Imputation Pipeline) — Repository Audit & Implementation Roadmap

Repository: `https://github.com/intanypurbasari/food-nutrition` (cloned at audit time, `main`)
Scope owner: Stage 3 — Machine Learning Imputation Pipeline
Author role: Principal ML Research Software Architect (planning only — no implementation code below)

---

## 1. Repository Audit

### 1.1 Top-level layout (as it exists today)

```text
config/          settings.py (scraper config only), __init__.py (empty package docstring)
data_raw/        tkpi_raw.csv/json, myfcd_raw.json (raw scrape output)
data_clean/      tkpi_clean.csv/json, myfcd_clean.csv/json (unified-schema, post-normalization)
data_processed/  entity-resolution + USDA-enrichment outputs (see 1.3)
docs/            narrative docs, data dictionary, workflow diagrams, missingness heatmaps
reports/         structured pipeline reports (quality, missing value, integration, correlation)
scripts/         CLI entry points + two Jupyter notebooks
src/             reusable Python modules (cleaning, schema, scrapers, validation)
tests/           pytest unit tests + CSV fixtures
app/             prototype.py — Streamlit prototype (out of Stage 3 scope)
usda-csv/        USDA SR Legacy reference tables (food.csv, food_nutrient.csv, nutrient.csv, ...)
logs/            empty, `.gitkeep` only — no logging is emitted anywhere yet
requirements.txt requests, beautifulsoup4, pandas, pydantic, streamlit, pytest, python-dotenv
```

**No `src/imputation/` module exists yet.** This is the primary gap Stage 3 must fill.

### 1.2 Completed modules (verified by reading source, not just README)

| Module | File(s) | What it actually does |
|---|---|---|
| Unified schema | `src/schema/nutrition_schema.py` | Pydantic `NutritionRecord`; defines the canonical **22 `NUTRIENT_FIELDS`**; `schema_columns()` helper |
| Cleaning utilities | `src/cleaning/normalizers.py` | `is_missing`, `normalize_numeric`, `normalize_column_name`, `normalize_food_name`, `normalize_category`, `compute_missing_nutrient_count`, `compute_completeness_score` |
| Quality checks | `src/validation/quality_checks.py` | `validate_dataframe`, `combine_quality_reports` — required-field, numeric-type, range, and completeness-consistency checks |
| Scrapers | `src/scrapers/base.py`, `tkpi_scraper.py`, `myfcd_scraper.py` | Ethical scraping (delay, limit, cache, fallback report) — irrelevant to Stage 3 |
| Cleaning scripts | `scripts/clean_tkpi.py`, `scripts/clean_myfcd.py` | Produce `data_clean/*_clean.csv` from raw scrape |
| Validation script | `scripts/validate_dataset.py` | Wraps `validate_dataframe`/`combine_quality_reports`, writes `reports/data_quality_report.{md,json}` |
| Merge script | `scripts/build_repository_sample.py` | Concatenates `data_clean/*_clean.csv` → `data_processed/nutrition_repository_sample.csv`, writes `reports/integration_summary.md` |
| Export script | `scripts/export_repository_json.py` | Flat/by-source/by-category JSON exports |
| Orchestrator | `scripts/run_pipeline.py` | Runs scrape → clean → validate → merge → export as subprocesses. **Does not yet call entity resolution, missingness diagnosis, or (future) imputation.** |
| Tests | `tests/test_normalizers.py`, `test_quality_checks.py`, `test_schema.py` | pytest, import from `src.*`, use `tests/fixtures/sample_fixture_{tkpi,myfcd}.csv` |

### 1.3 Entity Resolution output already available (Stage 1, Joyce — read-only input to Stage 3)

- `data_processed/tkpi_usda_links.csv`, `myfcd_usda_links.csv` — regional→USDA linkage (`source_food_id, ..., usda_fdc_id, ..., similarity_score, confidence`)
- `data_processed/tkpi_myfcd_links.csv` — direct TKPI↔MyFCD linkage, columns `tkpi_food_id, myfcd_food_id, similarity_score` (156 pairs)
- `data_processed/tkpi_myfcd_links_mutual.csv` — mutual-best subset, adds `confidence` column (52 pairs)
- `data_processed/tkpi_only_nonmatch.csv`, `myfcd_only_nonmatch.csv` — unmatched foods per source
- **`data_processed/tkpi_enriched.csv` / `myfcd_enriched.csv`** — this is the important one for Stage 3: the original 22-schema columns **plus 6 USDA value-borrowed columns**, each with a `_source` and `_confidence` suffix column:
  `magnesium_mg, sugars_total_g, saturated_fat_g, cholesterol_mg, vitamin_b6_mg, vitamin_b12_mcg` (+ `*_source`, `*_confidence` for each)
- Source code for this stage lives only as `scripts/entity_resolution_threeway.ipynb` (no `.py` counterpart exists in the repo, despite the README referencing `entity_resolution_threeway.py`). It is a **pure-numpy TF-IDF cosine matcher** (no sklearn dependency), category-blocked via a hand-written crosswalk dict, with HIGH/MEDIUM/LOW confidence thresholds (0.65 / 0.40).

### 1.4 Missing-Data Diagnosis output already available (Stage 2, Intan — read-only input to Stage 3)

- `reports/missing_corr_TKPI.csv`, `missing_corr_MyFCD.csv` — phi-coefficient correlation matrices of missingness indicators
- `reports/ringkasan_r_perbandingan.csv` — summarized r-values by nutrient group
- `reports/tkpi_missing_value_report.md`, `myfcd_missing_value_report.md` — per-nutrient missing count/percent (verified numbers: TKPI 1146 rows, MyFCD 234 rows)
- **`data_processed/availability_matrix.csv`** — the key routing table for Stage 3. Columns: `TKPI_terisi, TKPI_total, MyFCD_terisi, MyFCD_total, TKPI_pct, MyFCD_pct, kelompok, strategi_imputasi`. `strategi_imputasi` takes one of three values per nutrient: `"Imputasi internal per basis"`, `"Cross-DB transfer / USDA"`, `"Pinjam USDA (kosong di kedua basis)"`. **This file is the authoritative source for which imputation strategy applies to which nutrient** — Stage 3 code must read it rather than re-deriving the routing logic.
- Documented finding (README + notebook comments): TKPI missingness pattern = **MAR** (concentrated in mineral block), MyFCD = **MNAR/structural** (missing across the whole proximate panel).
- Source code lives only as `scripts/Analisis Pola Missingness.ipynb` (README calls it `analisis_pola_kehilangan.py`; no `.py` file exists in the repo). **The notebook hardcodes an absolute Windows path** (`C:\Users\intan\...`) — this is a real, existing defect, not something Stage 3 introduced; Stage 3 code must not repeat this pattern (all Stage 3 paths must be relative to repo root / config-driven, per the quality requirements already used elsewhere in `scripts/*.py` via `ROOT = Path(__file__).resolve().parents[1]`).

### 1.5 Placeholder / unfinished / inconsistent items found during audit

- `logs/` exists but is empty (`.gitkeep` only) — **no structured logging exists anywhere in the repo today**; every script uses bare `print(f"[STAGE] ...")`. Stage 3 should follow this existing convention rather than introducing a new logging framework unannounced, unless explicitly asked to add real logging (see Milestone 2).
- `requirements.txt` has **no ML/imputation dependencies** (no scikit-learn, no fancyimpute/missingpy/miceforest, no scipy, no matplotlib/seaborn — even though the missingness notebook already imports matplotlib/seaborn ad hoc). Stage 3 must add these explicitly and minimally.
- README references files that do not exist in the current tree: `tkpi_myfcd_links_detailed.csv`, `entity_resolution_threeway.py`, `analisis_pola_kehilangan.py`, `availability_matrix_TKPI_vs_MyFCD.csv` (actual filename is `availability_matrix.csv`). Treat the README as slightly aspirational/stale; **trust the actual files on disk**, which this audit used as source of truth.
- `docs/progress_report.md` predates the entity-resolution/missingness work (its "Rencana Lanjutan" section still lists entity matching and imputation as future work) — it is out of date and should eventually be refreshed, but that is a documentation task, not a blocker for Stage 3 code.
- `scripts/run_pipeline.py` does not invoke entity resolution, missingness diagnosis, or (once built) imputation — it only orchestrates the original scrape→clean→validate→merge→export chain. Extending it is in-scope for Stage 3 documentation/wiring but must be additive (new optional stage), not a rewrite.
- No `src/imputation/` package, no imputation config, no imputation tests, no imputation CLI scripts exist. This is 100% greenfield within Stage 3's boundary — nothing to "reuse-not-recreate" inside imputation itself, but everything around it (schema, normalizers, path conventions, print-based stage logging, pytest/fixture conventions, config pattern) must be reused.

### 1.6 Reusable utilities Stage 3 must build on top of (not duplicate)

- `src.schema.nutrition_schema.NUTRIENT_FIELDS` and `schema_columns()` — canonical column list/order
- `src.cleaning.normalizers.is_missing` — the repo's single definition of "what counts as missing" (handles `nan`, `""`, `"tr"`, `"trace"`, etc.) — imputers must treat missingness consistently with this, not with a bare `pd.isna()`
- `src.validation.quality_checks.validate_dataframe` — post-imputation output should remain schema-valid; Stage 3 should re-use this for a post-imputation validation pass rather than writing a parallel validator
- The `ROOT = Path(__file__).resolve().parents[1]` + `sys.path.insert(0, str(ROOT))` pattern used identically in every existing `scripts/*.py`
- The `print(f"[STAGE] ...")` stdout convention used by `run_pipeline.py` and all pipeline scripts
- `data_processed/availability_matrix.csv` as the imputation-strategy router (see 1.4)
- `data_processed/tkpi_enriched.csv` / `myfcd_enriched.csv` as the Stage 3 **input** files (already USDA-enriched — Stage 3 does not need to redo value borrowing, only consume the columns that are already there)
- `data_processed/tkpi_myfcd_links_mutual.csv` as the row-pairing table for the cross-database-transfer nutrients

---

## 2. Current Stage Analysis

| Stage | Owner | Status |
|---|---|---|
| Stage 1 — Entity Resolution | Joyce | **Done**, outputs on disk in `data_processed/` (see 1.3). Source only as notebook. |
| Stage 2 — Missing Data Diagnosis | Intan | **Done**, outputs on disk in `reports/` + `data_processed/availability_matrix.csv` (see 1.4). Source only as notebook. |
| Stage 3 — ML Imputation Pipeline | **You** | **Not started.** No `src/imputation/`, no imputation scripts, no imputation tests, no imputation dependencies declared. |
| Stage 4 — Evaluation | Fetty | Out of scope. Not inspected beyond confirming no `src/evaluation/` exists yet either. |

Stage 3 can begin immediately: its required inputs (`tkpi_enriched.csv`, `myfcd_enriched.csv`, `availability_matrix.csv`, `tkpi_myfcd_links_mutual.csv`) all exist and are populated with real data, not placeholders.

---

## 3. Stage 3 Dependency Graph

```text
[Stage 1 output: tkpi_enriched.csv, myfcd_enriched.csv, tkpi_myfcd_links_mutual.csv]
[Stage 2 output: availability_matrix.csv]
            │
            ▼
M1  chore(config): imputation dependencies + config + package scaffold
            │
            ▼
M2  feat(imputation): shared I/O, strategy-routing, and post-validation utilities
            │
   ┌────────┼─────────────┬───────────────┐
   ▼        ▼              ▼               ▼
M3        M4             M5              (M6 depends on M2 only,
Mean/     KNN            MICE             independent of M3-M5)
Median    baseline       baseline
baseline
   │        │              │
   └────────┴──────┬───────┘
                    ▼
M6  feat(missforest): within-database MissForest (per source)
                    │
                    ▼
M7  feat(missforest): cross-database MissForest transfer (TKPI → MyFCD)
                    │
                    ▼
M8  feat(imputation): USDA value-borrowing pass-through + integrated dataset assembly
                    │
                    ▼
M9  feat(imputation): evaluation-ready long-format export (all methods, for Stage 4)
                    │
                    ▼
M10 test(imputation): unit tests for all imputation modules + reproducibility checks
                    │
                    ▼
M11 docs(stage3): documentation + optional run_pipeline.py wiring
```

**Independence notes:**
- M3, M4, M5 (the three baselines) are mutually independent once M2 exists — Claude Code could run them in parallel across sessions if desired, but each still gets its own prompt/commit per the "one feature, one commit" rule.
- M6 (within-database MissForest) only depends on M2, not on M3–M5, since baselines and MissForest are alternative methods, not a pipeline chain. It is sequenced after the baselines here only to keep the roadmap narrative simple; Claude Code may be run on M6 immediately after M2 if you prefer.
- M7 (cross-database transfer) depends on M6 because it reuses the same MissForest fitting utility, just applied to a different train/apply split.
- M8 depends on M3–M7 because "integrated dataset" means one row per food with the best available value from baseline/MissForest/cross-transfer/USDA-borrowed columns, per the `strategi_imputasi` routing in `availability_matrix.csv`.
- M9 depends on M8 (needs the integrated dataset) and also independently needs M3–M7's per-method outputs (needs all candidate values, not just the winning one, so Stage 4 can compare methods).
- M10 depends on everything it tests (M2–M9) existing.
- M11 depends on the whole pipeline being functionally complete.

---

## 4. Stage 3 Architecture (target end-state, additive only)

```text
config/
  imputation_settings.py        [NEW] paths, nutrient groupings, random seed, method params

src/
  imputation/                   [NEW package]
    __init__.py
    io_utils.py                 load enriched CSVs, read availability_matrix strategy, write outputs
    baselines.py                mean / median / KNN imputers
    mice_imputer.py             MICE baseline
    missforest_imputer.py       within-database MissForest
    cross_transfer.py           cross-database MissForest transfer (TKPI → MyFCD)
    integrate.py                assembles final integrated dataset per availability_matrix strategy
    evaluation_export.py        long-format, evaluation-ready export for Stage 4

scripts/
  run_baseline_imputation.py    [NEW] CLI: mean/median/knn/mice
  run_missforest_imputation.py  [NEW] CLI: within-db + cross-db transfer
  run_integration.py            [NEW] CLI: builds final integrated + evaluation-ready outputs

data_processed/                 [NEW files only, existing files untouched]
  tkpi_imputed_baseline.csv, myfcd_imputed_baseline.csv
  tkpi_imputed_missforest.csv, myfcd_imputed_missforest.csv
  myfcd_imputed_crossdb.csv
  nutrition_repository_imputed.csv         <- final integrated dataset
  nutrition_repository_imputed_long.csv    <- evaluation-ready long format

reports/
  imputation_summary.md         [NEW]
  imputation_method_comparison.csv  [NEW]

tests/
  test_imputation_io.py, test_baselines.py, test_missforest.py, test_integration.py  [NEW]
  fixtures/sample_fixture_enriched_tkpi.csv, sample_fixture_enriched_myfcd.csv        [NEW]

docs/
  stage3_imputation.md          [NEW]
```

Nothing under `data_raw/`, `data_clean/`, the existing `data_processed/*` files, `src/scrapers/`, `src/cleaning/`, `src/validation/`, `src/schema/`, `app/`, or `usda-csv/` is modified by any milestone below.

---

## Milestone 1 — Imputation dependencies, config, and package scaffold

**Purpose:** Establish the minimum ground truth (dependencies, config, empty package) every later milestone needs, without writing any imputation logic yet.

**Existing files to inspect:**
- `requirements.txt`
- `config/settings.py`, `config/__init__.py`
- `src/__init__.py`, `src/schema/__init__.py` (as a package-init style reference)
- `scripts/run_pipeline.py` (for the `ROOT = Path(__file__).resolve().parents[1]` convention)

**Files to modify:**
- `requirements.txt` (append only — do not remove or reorder existing entries)
- Create `config/imputation_settings.py`
- Create `src/imputation/__init__.py`

**Files forbidden to touch:** everything else in the repository, including `config/settings.py` itself (append to `requirements.txt`, don't touch scraper config).

**Deliverables:**
- `requirements.txt` gains: `scikit-learn`, `scipy`, plus whatever MissForest implementation is chosen (document the choice — e.g. `missingpy` or a hand-rolled `IterativeImputer(estimator=RandomForestRegressor)` if `missingpy` is unmaintained/incompatible; Claude Code must check current PyPI availability before deciding and note the decision in the commit body).
- `config/imputation_settings.py` containing: repo-relative path constants for `data_processed/tkpi_enriched.csv`, `myfcd_enriched.csv`, `availability_matrix.csv`, `tkpi_myfcd_links_mutual.csv`, and the new output paths listed in Section 4; `RANDOM_SEED = 42`; nutrient group lists imported from or mirrored consistently with `src/schema/nutrition_schema.NUTRIENT_FIELDS` (must not hardcode a second, divergent nutrient list).
- `src/imputation/__init__.py` with a one-line module docstring, matching the style of `src/cleaning/__init__.py`.

**Definition of Done:** `pip install -r requirements.txt` succeeds; `python -c "import config.imputation_settings"` succeeds; no existing test breaks (`pytest` still green); no existing file's behavior changes.

**Semantic Commit:** `chore(config): add imputation dependencies and Stage 3 configuration scaffold`

**Claude Code Prompt:**
```
Objective: Add Stage 3 (ML imputation) dependencies and a configuration/package
scaffold to the food-nutrition repository, without implementing any imputation
logic yet.

Repository context: This is an academic research repo for a food-composition
data pipeline. Stage 1 (entity resolution) and Stage 2 (missing-data diagnosis)
are already complete, with outputs in data_processed/ and reports/. Stage 3
(machine learning imputation) has not started. You are ONLY doing groundwork
in this milestone.

Read these files first:
- requirements.txt
- config/settings.py
- config/__init__.py
- src/__init__.py
- src/cleaning/__init__.py
- scripts/run_pipeline.py (note the `ROOT = Path(__file__).resolve().parents[1]`
  pattern used for repo-relative paths — reuse this exact pattern)

Reuse these utilities:
- The repo-root path pattern from scripts/run_pipeline.py.
- src/schema/nutrition_schema.py's NUTRIENT_FIELDS list as the single source of
  truth for nutrient column names — do not hardcode a second, divergent list.

Modify only:
- requirements.txt (append new dependencies at the end; do not reorder or
  remove existing lines)
- Create config/imputation_settings.py
- Create src/imputation/__init__.py

Do not touch:
- config/settings.py (scraper config; leave untouched)
- Any file under data_raw/, data_clean/, data_processed/, reports/, app/,
  src/scrapers/, src/cleaning/, src/validation/, src/schema/, usda-csv/
- scripts/run_pipeline.py (wiring it up is a later milestone)

Expected implementation boundaries:
- Add to requirements.txt: scikit-learn, scipy, and a MissForest-capable
  package. Check current PyPI availability/maintenance status before choosing
  between `missingpy` and a hand-built IterativeImputer(RandomForestRegressor)
  approach from scikit-learn; document your choice and reasoning in the commit
  message body.
- config/imputation_settings.py must define, as module-level constants:
  - Repo-relative Path objects (built the same way scripts/run_pipeline.py
    builds ROOT) for: data_processed/tkpi_enriched.csv,
    data_processed/myfcd_enriched.csv, data_processed/availability_matrix.csv,
    data_processed/tkpi_myfcd_links_mutual.csv
  - Output path constants for the new files this Stage will eventually produce
    (baseline, missforest, cross-db, integrated, evaluation-long outputs under
    data_processed/, plus reports/imputation_summary.md and
    reports/imputation_method_comparison.csv) — paths only, nothing needs to
    exist on disk yet
  - RANDOM_SEED = 42
  - A reference to NUTRIENT_FIELDS from src.schema.nutrition_schema (import it,
    do not copy/paste the list)
- src/imputation/__init__.py: a short module docstring only, styled like
  src/cleaning/__init__.py. No other code.
- No absolute paths anywhere (this repo has a known defect where one notebook
  hardcodes a Windows absolute path — do not repeat that pattern).

Expected outputs: requirements.txt updated; config/imputation_settings.py;
src/imputation/__init__.py. No data files are created or modified.

Validation requirements: `pip install -r requirements.txt` must succeed in a
clean environment. `python -c "import config.imputation_settings"` must
succeed without errors.

Testing requirements: Run the existing test suite (`pytest`) and confirm it
is still 100% green — this milestone must not break anything. No new tests
are required yet (testing utilities/config directly is covered in Milestone 10).

Documentation requirements: None yet (covered in Milestone 11).

Logging requirements: None (no runtime code yet).

Coding standards: PEP8, type hints on any function signatures you add,
no hardcoded absolute paths, config-driven.

Definition of Done: pip install succeeds; import succeeds; full existing
pytest suite still passes; git diff touches only the files listed above.

What must NOT be changed: config/settings.py, any file under data_raw/,
data_clean/, data_processed/, reports/, app/, src/scrapers/, src/cleaning/,
src/validation/, src/schema/, usda-csv/, and scripts/run_pipeline.py.

End with one commit:
chore(config): add imputation dependencies and Stage 3 configuration scaffold
```

---

## Milestone 2 — Shared imputation I/O, strategy-routing, and post-validation utilities

**Purpose:** Build the single shared module every imputer will call to load inputs, look up which imputation strategy applies to which nutrient (from `availability_matrix.csv`), and validate/write outputs — so no later milestone reimplements I/O or routing logic.

**Existing files to inspect:**
- `data_processed/availability_matrix.csv` (columns: `TKPI_terisi, TKPI_total, MyFCD_terisi, MyFCD_total, TKPI_pct, MyFCD_pct, kelompok, strategi_imputasi`)
- `data_processed/tkpi_enriched.csv`, `myfcd_enriched.csv` (input schemas — 22 base nutrients + 6 USDA-borrowed columns with `_source`/`_confidence` suffixes)
- `scripts/build_repository_sample.py` and `scripts/validate_dataset.py` (for the `load_*`/error-handling style: check file exists, check non-empty, `print(f"[...] ...")` status lines)
- `src/validation/quality_checks.py` (`validate_dataframe`, to be reused for post-imputation validation)
- `src/cleaning/normalizers.py` (`is_missing`, to be reused as the canonical missingness check)
- `config/imputation_settings.py` (created in Milestone 1)

**Files to modify:**
- Create `src/imputation/io_utils.py`

**Files forbidden to touch:** everything else, including `data_processed/availability_matrix.csv` itself (read-only input).

**Deliverables:**
- `load_enriched(source: str) -> pd.DataFrame` — loads `tkpi_enriched.csv` or `myfcd_enriched.csv` with the same existence/empty-file guard style as `scripts/build_repository_sample.py`'s `load_clean`.
- `load_availability_matrix() -> pd.DataFrame` and `get_strategy(nutrient: str) -> str` — returns one of the three literal strategy strings found in the real data (`"Imputasi internal per basis"`, `"Cross-DB transfer / USDA"`, `"Pinjam USDA (kosong di kedua basis)"`); raise a clear error for unknown nutrients rather than silently defaulting.
- `load_mutual_links() -> pd.DataFrame` — loads `tkpi_myfcd_links_mutual.csv` for the cross-database transfer milestone.
- `validate_imputed_output(df, source_name) -> dict` — thin wrapper that calls `src.validation.quality_checks.validate_dataframe` on the imputed frame and additionally asserts zero remaining `is_missing()` values in whichever nutrient columns the caller declares were targeted for imputation.
- `write_output(df, path)` — CSV writer following the `to_csv(..., index=False, encoding="utf-8")` convention already used by `build_repository_sample.py`.

**Definition of Done:** module imports cleanly; manually loading both enriched files and the availability matrix through the new functions returns non-empty DataFrames with the expected columns; `get_strategy` returns correct values for at least one nutrient from each of the three strategy buckets (e.g. `iron_mg` → internal, `carotene_total_mcg` → cross-DB/USDA, `vitamin_a_mcg` → USDA-borrow).

**Semantic Commit:** `feat(imputation): add shared I/O, strategy-routing, and validation utilities`

**Claude Code Prompt:**
```
Objective: Build the shared I/O, availability-matrix strategy-routing, and
post-imputation validation utility module that every Stage 3 imputer will
depend on. Implement utilities only — no actual imputation algorithm in this
milestone.

Repository context: food-nutrition repo, Stage 3 in progress. Milestone 1
already added config/imputation_settings.py (path constants, RANDOM_SEED) and
an empty src/imputation package. This milestone adds the shared I/O layer.

Read these files first:
- config/imputation_settings.py
- data_processed/availability_matrix.csv (inspect actual column names and the
  three distinct values of the strategi_imputasi column)
- data_processed/tkpi_enriched.csv and myfcd_enriched.csv (inspect header row
  to confirm the 22 base nutrient columns plus magnesium_mg, sugars_total_g,
  saturated_fat_g, cholesterol_mg, vitamin_b6_mg, vitamin_b12_mcg and their
  _source/_confidence companions)
- data_processed/tkpi_myfcd_links_mutual.csv (columns: tkpi_food_id,
  myfcd_food_id, similarity_score, confidence)
- scripts/build_repository_sample.py (specifically the load_clean function —
  match its existence/empty-file guard style and its print(f"[MERGE] ...")
  logging style, adapted to an "[IMPUTE]" tag)
- scripts/validate_dataset.py (for the pattern of calling into
  src/validation/quality_checks.py)
- src/validation/quality_checks.py (validate_dataframe, combine_quality_reports
  — reuse validate_dataframe, do not reimplement it)
- src/cleaning/normalizers.py (is_missing — reuse this exact function as the
  canonical missingness check; do not use a bare pd.isna() instead)
- src/schema/nutrition_schema.py (NUTRIENT_FIELDS)

Reuse these utilities:
- src.validation.quality_checks.validate_dataframe
- src.cleaning.normalizers.is_missing
- config.imputation_settings path constants and RANDOM_SEED
- The ROOT / sys.path.insert pattern already used throughout scripts/*.py

Modify only:
- Create src/imputation/io_utils.py

Do not touch:
- data_processed/availability_matrix.csv, tkpi_enriched.csv, myfcd_enriched.csv,
  tkpi_myfcd_links_mutual.csv (read-only inputs)
- Any file modified in Milestone 1 except adding this new file
- Anything outside src/imputation/

Expected implementation boundaries — implement these functions in
src/imputation/io_utils.py:
- load_enriched(source: str) -> pd.DataFrame — source is "TKPI" or "MyFCD";
  loads the corresponding *_enriched.csv via the path constants from
  config.imputation_settings; guard for missing/empty file the same way
  build_repository_sample.load_clean does, printing "[IMPUTE] ..." on skip;
  raise a clear exception if the required file is absent (imputation cannot
  proceed silently the way merge-of-optional-sources can).
- load_availability_matrix() -> pd.DataFrame — loads availability_matrix.csv,
  using the nutrient name as the index (it's the unnamed first column).
- get_strategy(nutrient: str) -> str — looks up strategi_imputasi for a given
  nutrient column name; raise KeyError with a clear message if the nutrient
  is not present in the matrix, rather than defaulting silently.
- load_mutual_links() -> pd.DataFrame — loads
  tkpi_myfcd_links_mutual.csv unchanged.
- validate_imputed_output(df: pd.DataFrame, source_name: str,
  targeted_columns: list[str]) -> dict — calls
  src.validation.quality_checks.validate_dataframe(df, source_name) and
  additionally checks that none of targeted_columns still contain values for
  which src.cleaning.normalizers.is_missing() is True; include this as an
  extra key (e.g. "remaining_missing_in_targeted_columns") in the returned
  dict rather than silently passing/failing.
- write_output(df: pd.DataFrame, path: Path) -> None — df.to_csv(path,
  index=False, encoding="utf-8"), creating the parent directory if needed
  (mkdir(parents=True, exist_ok=True)), matching existing scripts' style.

Expected outputs: src/imputation/io_utils.py only. No data files are written
by running this module on its own (these are library functions, not a script
with a __main__ block).

Validation requirements: Manually verify (e.g. in a throwaway python -c
snippet you run and then discard) that load_enriched("TKPI") and
load_enriched("MyFCD") return non-empty DataFrames with the expected 22+12
columns, that get_strategy("iron_mg"), get_strategy("carotene_total_mcg"),
and get_strategy("vitamin_a_mcg") return the three distinct real strategy
strings found in availability_matrix.csv, and that load_mutual_links()
returns a non-empty DataFrame with columns tkpi_food_id, myfcd_food_id.

Testing requirements: No test file yet (Milestone 10 covers imputation
tests comprehensively) — but do not break the existing pytest suite.

Documentation requirements: Add a short module-level docstring to
io_utils.py explaining its role as the shared I/O/routing layer for Stage 3.

Logging requirements: Follow the existing "[TAG] message" print-based
convention (use "[IMPUTE]") — do not introduce a new logging framework.

Coding standards: PEP8, full type hints, docstrings on every public function,
no hardcoded paths (everything via config.imputation_settings), reuse
existing utilities rather than reimplementing them.

Definition of Done: module imports cleanly with no errors; all five functions
behave as specified above when manually exercised; full existing pytest
suite still passes.

What must NOT be changed: any file outside src/imputation/io_utils.py, and
none of the data_processed/ or reports/ input files.

End with one commit:
feat(imputation): add shared I/O, strategy-routing, and validation utilities
```

---

## Milestone 3 — Mean & Median baseline imputers

**Purpose:** First concrete imputation method (per RESEARCH OBJECTIVE: "Mean baseline, Median baseline"), applied per-source (TKPI imputed from TKPI's own distribution, MyFCD from its own), restricted to nutrients whose strategy is `"Imputasi internal per basis"`.

**Existing files to inspect:**
- `src/imputation/io_utils.py` (Milestone 2)
- `config/imputation_settings.py`
- `data_processed/tkpi_enriched.csv`, `myfcd_enriched.csv`
- `reports/tkpi_missing_value_report.md`, `myfcd_missing_value_report.md` (to sanity-check expected missing counts per column before/after)

**Files to modify:**
- Create `src/imputation/baselines.py`
- Create `scripts/run_baseline_imputation.py`

**Files forbidden to touch:** `src/imputation/io_utils.py` (call it, don't modify it, unless a genuine bug is found — if so, document why in the commit body).

**Deliverables:**
- `mean_impute(df, columns) -> pd.DataFrame` and `median_impute(df, columns) -> pd.DataFrame` in `src/imputation/baselines.py`, operating only on the given `columns` (restrict to nutrients with strategy `"Imputasi internal per basis"`, looked up via `io_utils.get_strategy`), fit-and-transform on the same source's own data (no cross-source leakage).
- `scripts/run_baseline_imputation.py` — CLI (`--method {mean,median}`, default runs both) that: loads TKPI and MyFCD via `io_utils.load_enriched`, determines target columns via `io_utils.get_strategy`, imputes each source independently, validates via `io_utils.validate_imputed_output`, writes `data_processed/tkpi_imputed_baseline.csv` / `myfcd_imputed_baseline.csv` via `io_utils.write_output`.

**Definition of Done:** running `python scripts/run_baseline_imputation.py` produces both output CSVs with zero remaining missing values in the targeted columns (verified via `validate_imputed_output`); columns outside the `"Imputasi internal per basis"` strategy are left untouched (still missing where they were missing).

**Semantic Commit:** `feat(baseline): add mean and median imputation for internally-imputable nutrients`

**Claude Code Prompt:**
```
Objective: Implement mean and median baseline imputation for nutrients whose
Stage-2-assigned strategy is "internal per-source imputation", using the
shared I/O layer from Milestone 2.

Repository context: food-nutrition repo, Stage 3 in progress. src/imputation
now has __init__.py and io_utils.py (load_enriched, load_availability_matrix,
get_strategy, load_mutual_links, validate_imputed_output, write_output).
config/imputation_settings.py has path constants and RANDOM_SEED=42.

Read these files first:
- src/imputation/io_utils.py (use its functions, do not duplicate logic)
- config/imputation_settings.py
- data_processed/availability_matrix.csv (confirm which nutrients have
  strategi_imputasi == "Imputasi internal per basis" — these are the only
  columns this milestone touches)
- reports/tkpi_missing_value_report.md and myfcd_missing_value_report.md
  (for sanity-checking expected before/after missing counts)
- scripts/validate_dataset.py and scripts/build_repository_sample.py (for the
  argparse-free, function-based main() with `raise SystemExit(main())` style
  used throughout scripts/, and the ROOT/sys.path pattern)

Reuse these utilities:
- src.imputation.io_utils.load_enriched, get_strategy,
  validate_imputed_output, write_output
- src.cleaning.normalizers.is_missing (via io_utils, indirectly — do not
  reimplement missingness detection)

Modify only:
- Create src/imputation/baselines.py
- Create scripts/run_baseline_imputation.py

Do not touch:
- src/imputation/io_utils.py, config/imputation_settings.py (call them,
  don't edit them, unless you find an actual bug — if so, explain why in the
  commit body)
- data_processed/tkpi_enriched.csv, myfcd_enriched.csv (read-only inputs)
- Any file outside the two new files listed above

Expected implementation boundaries:
- src/imputation/baselines.py:
  - mean_impute(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame — for
    each column, fill missing values (per src.cleaning.normalizers.is_missing
    semantics, applied via the already-loaded numeric column) with that
    column's own mean computed from non-missing values in df; return a copy,
    do not mutate the input in place.
  - median_impute(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame —
    same as above but with median.
  - Both functions must only touch the given columns list — every other
    column in df passes through unchanged.
  - Do not impute a column for one source using statistics from the other
    source (TKPI and MyFCD are imputed independently, called separately by
    the script).
- scripts/run_baseline_imputation.py:
  - argparse with --method choices ["mean", "median"], default: run both
    sequentially.
  - For each source in ["TKPI", "MyFCD"]: load via io_utils.load_enriched,
    determine target columns by calling io_utils.get_strategy(nutrient) for
    every nutrient in src.schema.nutrition_schema.NUTRIENT_FIELDS and keeping
    only those whose strategy equals "Imputasi internal per basis", run the
    selected method(s), validate via io_utils.validate_imputed_output with
    that column list as targeted_columns, and write outputs via
    io_utils.write_output to config.imputation_settings' baseline output path
    constants (e.g. tkpi_imputed_baseline.csv / myfcd_imputed_baseline.csv —
    use whatever names Milestone 1 assigned in config/imputation_settings.py).
  - Print "[IMPUTE] ..." status lines mirroring the style of
    scripts/build_repository_sample.py / scripts/validate_dataset.py.
  - main() returns 0/1 the same way other scripts/*.py do, with
    `if __name__ == "__main__": raise SystemExit(main())`.

Expected outputs: data_processed/tkpi_imputed_baseline.csv,
data_processed/myfcd_imputed_baseline.csv (only when the script is run —
do not commit generated CSVs unless the repository's existing convention is
to commit data_processed/ outputs, which it is here based on existing
tracked files; check `git status` after running and follow whatever the
repo's existing tracked/untracked pattern for data_processed/ is).

Validation requirements: After running the script, confirm via
io_utils.validate_imputed_output (already called inside the script) that
"Imputasi internal per basis" columns have zero remaining missing values,
and manually spot-check that a column NOT in that strategy bucket (e.g.
vitamin_a_mcg) is still fully missing/untouched in the output.

Testing requirements: Do not add tests yet (Milestone 10). Confirm the
existing pytest suite still passes.

Documentation requirements: Docstrings on mean_impute and median_impute
explaining the per-source, per-strategy scope.

Logging requirements: "[IMPUTE] ..." print statements, matching existing
scripts' style — no new logging framework.

Coding standards: PEP8, type hints, RANDOM_SEED from config used wherever
randomness could matter (mean/median are deterministic, but pass/document
the seed anyway for consistency with later stochastic methods), no
hardcoded paths, no duplicated logic versus io_utils.

Definition of Done: script runs end-to-end without error; output CSVs exist
with zero missing values in targeted columns and unchanged missingness in
non-targeted columns; existing pytest suite is green.

What must NOT be changed: src/imputation/io_utils.py, config files, any
existing data_processed/ or reports/ file.

End with one commit:
feat(baseline): add mean and median imputation for internally-imputable nutrients
```

---

## Milestone 4 — KNN baseline imputer

**Purpose:** Second baseline method (RESEARCH OBJECTIVE: "KNN baseline"), same scope rules as Milestone 3 but using multivariate nearest-neighbor imputation, which can use correlations between nutrients (unlike mean/median).

**Existing files to inspect:**
- `src/imputation/baselines.py` (Milestone 3 — extend this file, same module, don't create a parallel one)
- `src/imputation/io_utils.py`
- `config/imputation_settings.py`
- `reports/missing_corr_TKPI.csv`, `missing_corr_MyFCD.csv` (context for why a multivariate method is worth comparing against mean/median)

**Files to modify:**
- `src/imputation/baselines.py` (add `knn_impute`, do not touch `mean_impute`/`median_impute`)
- `scripts/run_baseline_imputation.py` (add `"knn"` to `--method` choices)

**Files forbidden to touch:** `mean_impute`/`median_impute` function bodies; `src/imputation/io_utils.py`.

**Deliverables:**
- `knn_impute(df, columns, n_neighbors=5) -> pd.DataFrame` using `sklearn.impute.KNNImputer`, fit only on the numeric nutrient columns of the given source (not mixing TKPI/MyFCD rows), with `RANDOM_SEED` applied wherever the method accepts a seed-relevant parameter (KNNImputer itself is deterministic given fixed data/k, so document that no seed is needed, rather than passing a nonexistent parameter).
- `scripts/run_baseline_imputation.py` updated so `--method knn` (or default "run all three") also writes `tkpi_imputed_baseline.csv`/`myfcd_imputed_baseline.csv` correctly if multiple methods are run in the same invocation — clarify in this prompt whether multiple methods write to separate suffixed files (`_mean`, `_median`, `_knn`) or a combined file; **the roadmap decision: separate suffixed files per method**, so Milestone 9's evaluation-ready export can compare them.

**Definition of Done:** `python scripts/run_baseline_imputation.py --method knn` produces `data_processed/tkpi_imputed_baseline_knn.csv` / `myfcd_imputed_baseline_knn.csv` with zero missing values in targeted columns.

**Semantic Commit:** `feat(baseline): add KNN imputation baseline`

**Claude Code Prompt:**
```
Objective: Add a KNN-based multivariate imputation baseline, and refactor the
baseline runner's output naming so each method (mean/median/knn) writes its
own suffixed output file rather than overwriting a shared one.

Repository context: food-nutrition repo, Stage 3 in progress.
src/imputation/baselines.py currently has mean_impute and median_impute.
scripts/run_baseline_imputation.py currently writes
data_processed/tkpi_imputed_baseline.csv / myfcd_imputed_baseline.csv
regardless of --method. This milestone adds knn_impute and changes the
output filenames to be per-method (e.g. _mean, _median, _knn suffixes) so
that Milestone 9's evaluation-ready export can later compare all baseline
methods side by side.

Read these files first:
- src/imputation/baselines.py (existing mean_impute, median_impute — match
  their signature style and docstring style exactly)
- scripts/run_baseline_imputation.py (existing argparse/main structure)
- src/imputation/io_utils.py (load_enriched, get_strategy,
  validate_imputed_output, write_output)
- config/imputation_settings.py

Reuse these utilities:
- src.imputation.io_utils (all functions)
- The existing mean_impute/median_impute functions as a style/signature
  reference for knn_impute

Modify only:
- src/imputation/baselines.py — add knn_impute; do not alter the bodies of
  mean_impute or median_impute (only touch import lines if a new import is
  needed at the top of the file)
- scripts/run_baseline_imputation.py — add "knn" to the --method choices,
  and update output-path logic so each method writes to its own suffixed
  file (e.g. {source}_imputed_baseline_{method}.csv) instead of a shared
  filename

Do not touch:
- src/imputation/io_utils.py
- config/imputation_settings.py (unless you need to add new path constants
  for the suffixed baseline filenames — if so, ADD constants, do not remove
  or rename the ones from Milestone 1/3)
- The internal logic of mean_impute/median_impute

Expected implementation boundaries:
- knn_impute(df: pd.DataFrame, columns: list[str], n_neighbors: int = 5) ->
  pd.DataFrame — uses sklearn.impute.KNNImputer fit_transform restricted to
  the given columns only (do not let KNNImputer see or be influenced by
  non-nutrient columns like food_id or category); returns a copy of df with
  only those columns replaced; every other column passes through unchanged;
  same "Imputasi internal per basis" column-selection rule as Milestone 3,
  applied by the calling script, not hardcoded inside knn_impute itself
  (knn_impute should just take whatever columns list it's given, same
  contract as mean_impute/median_impute).
- Note in a docstring that KNNImputer is deterministic for fixed data and k
  (no random_state parameter exists on KNNImputer), so RANDOM_SEED from
  config is not applicable here — do not invent a fake seed parameter.
- Update scripts/run_baseline_imputation.py so that when multiple methods
  are requested (including the default "run all"), each writes its own file;
  add path constants to config/imputation_settings.py if the existing ones
  from Milestone 1 were singular (not per-method) — keep the Milestone 3
  mean/median outputs consistent with this new per-method naming (rename
  their constants too if necessary, and note in the commit body that this
  supersedes Milestone 3's filenames).

Expected outputs: data_processed/tkpi_imputed_baseline_mean.csv,
_median.csv, _knn.csv and the MyFCD equivalents (six files total after this
milestone, once the script is re-run).

Validation requirements: Run `python scripts/run_baseline_imputation.py`
with no --method flag (should run all three) and confirm all six output
files exist with zero missing values in targeted columns via
io_utils.validate_imputed_output.

Testing requirements: Do not add tests yet (Milestone 10). Confirm existing
pytest suite still passes.

Documentation requirements: Docstring on knn_impute explaining the
deterministic-given-k note above.

Logging requirements: "[IMPUTE] ..." print style, consistent with
Milestone 3.

Coding standards: PEP8, type hints, no hardcoded paths, no duplicated column
-selection logic (reuse the same "look up strategy for every NUTRIENT_FIELDS
entry" approach already written in Milestone 3's script — extract it to a
small helper function in the script if it would otherwise be duplicated
three times for mean/median/knn).

Definition of Done: all six baseline output files are produced correctly on
a clean run; existing pytest suite is green; mean_impute/median_impute
behavior is provably unchanged (their function bodies are untouched).

What must NOT be changed: mean_impute/median_impute logic, io_utils.py,
any data_processed/ file other than the new/renamed baseline outputs.

End with one commit:
feat(baseline): add KNN imputation baseline
```

---

## Milestone 5 — MICE baseline imputer

**Purpose:** Third baseline method (RESEARCH OBJECTIVE: "MICE baseline") — multivariate imputation by chained equations, via `sklearn.impute.IterativeImputer`.

**Existing files to inspect:**
- `src/imputation/baselines.py`
- `scripts/run_baseline_imputation.py`
- `config/imputation_settings.py` (for `RANDOM_SEED`)

**Files to modify:**
- `src/imputation/baselines.py` (add `mice_impute`) **or** a new `src/imputation/mice_imputer.py` — **decision for this roadmap: keep it in `baselines.py`** alongside mean/median/knn, since all four are "baseline" methods per the RESEARCH OBJECTIVE wording, reserving a separate module only for MissForest (which is the actual novel/complex method).
- `scripts/run_baseline_imputation.py` (add `"mice"` to `--method` choices, same suffixed-output pattern as Milestone 4)

**Files forbidden to touch:** `mean_impute`, `median_impute`, `knn_impute` bodies.

**Deliverables:**
- `mice_impute(df, columns, random_state=None) -> pd.DataFrame` using `sklearn.experimental.enable_iterative_imputer` + `sklearn.impute.IterativeImputer`, with `random_state` sourced from `config.imputation_settings.RANDOM_SEED` for reproducibility, converging with a documented `max_iter`.

**Definition of Done:** `python scripts/run_baseline_imputation.py --method mice` produces `data_processed/tkpi_imputed_baseline_mice.csv` / `myfcd_imputed_baseline_mice.csv` with zero missing values in targeted columns; re-running produces byte-identical results (reproducibility, given fixed seed).

**Semantic Commit:** `feat(baseline): add MICE imputation baseline`

**Claude Code Prompt:**
```
Objective: Add a MICE (Multiple Imputation by Chained Equations) baseline
using scikit-learn's IterativeImputer, reproducible via the shared
RANDOM_SEED.

Repository context: food-nutrition repo, Stage 3 in progress.
src/imputation/baselines.py has mean_impute, median_impute, knn_impute.
scripts/run_baseline_imputation.py supports --method {mean,median,knn} plus
a default "run all", each writing its own suffixed output file.

Read these files first:
- src/imputation/baselines.py (match existing function signature/docstring
  style exactly for the new mice_impute function)
- scripts/run_baseline_imputation.py (match the existing per-method output
  file naming and argparse pattern)
- config/imputation_settings.py (RANDOM_SEED)

Reuse these utilities:
- src.imputation.io_utils (load_enriched, get_strategy,
  validate_imputed_output, write_output)
- config.imputation_settings.RANDOM_SEED
- The same column-selection helper introduced/used in Milestone 4 for
  "Imputasi internal per basis" nutrients — do not reimplement it a fourth
  time.

Modify only:
- src/imputation/baselines.py — add mice_impute; do not alter
  mean_impute/median_impute/knn_impute bodies
- scripts/run_baseline_imputation.py — add "mice" to --method choices and
  wire it into the same per-method output-writing loop as mean/median/knn

Do not touch:
- src/imputation/io_utils.py, config/imputation_settings.py (read RANDOM_SEED,
  don't modify the file unless adding new path constants for the mice output
  files, in which case ADD, don't rename existing ones)
- mean_impute, median_impute, knn_impute function bodies

Expected implementation boundaries:
- mice_impute(df: pd.DataFrame, columns: list[str], random_state: int | None
  = None) -> pd.DataFrame — import `from sklearn.experimental import
  enable_iterative_imputer` before `from sklearn.impute import
  IterativeImputer` (required by scikit-learn's API); default random_state to
  config.imputation_settings.RANDOM_SEED when None is passed in from the
  caller; fit_transform restricted to `columns` only, same
  all-other-columns-pass-through contract as the other three functions;
  choose and document a max_iter (e.g. 10) and note convergence behavior is
  not separately verified by this function — that belongs in evaluation
  (Stage 4), not here.
- Update scripts/run_baseline_imputation.py's --method choices to
  ["mean", "median", "knn", "mice"], with the same "run all when omitted"
  default behavior, writing data_processed/tkpi_imputed_baseline_mice.csv
  and the MyFCD equivalent through io_utils.write_output.

Expected outputs: data_processed/tkpi_imputed_baseline_mice.csv,
data_processed/myfcd_imputed_baseline_mice.csv (in addition to the six files
from Milestone 4, for eight total baseline output files).

Validation requirements: Run the script twice in a row with --method mice
and confirm the two output files are identical (reproducibility given the
fixed RANDOM_SEED) — use a checksum or DataFrame equality check as part of
your manual verification, not as a new pytest test yet.

Testing requirements: Do not add tests yet (Milestone 10). Confirm existing
pytest suite still passes.

Documentation requirements: Docstring on mice_impute explaining the
IterativeImputer/enable_iterative_imputer requirement and the chosen
max_iter.

Logging requirements: "[IMPUTE] ..." print style consistent with prior
milestones.

Coding standards: PEP8, type hints, no hardcoded paths, no duplicated
column-selection logic across the four baseline methods in the script.

Definition of Done: script runs mice successfully; output is reproducible
given the fixed seed; existing pytest suite green; other three baseline
functions provably unchanged.

What must NOT be changed: mean_impute, median_impute, knn_impute bodies,
io_utils.py, existing data_processed/ files.

End with one commit:
feat(baseline): add MICE imputation baseline
```

---

## Milestone 6 — Within-database MissForest imputer

**Purpose:** The project's primary novel method (RESEARCH OBJECTIVE: "MissForest") — random-forest-based iterative imputation, fit and applied within a single source (no cross-database transfer yet — that's Milestone 7).

**Existing files to inspect:**
- `src/imputation/io_utils.py`
- `src/imputation/baselines.py` (for function-signature/docstring conventions to mirror, even though this is a new file)
- `config/imputation_settings.py`
- Milestone 1's dependency decision (whichever MissForest-capable package was chosen)

**Files to modify:**
- Create `src/imputation/missforest_imputer.py`
- Create `scripts/run_missforest_imputation.py`

**Files forbidden to touch:** `src/imputation/baselines.py`, `src/imputation/io_utils.py`.

**Deliverables:**
- `missforest_impute(df, columns, random_state=None) -> pd.DataFrame` — within-source MissForest (via the package chosen in Milestone 1), applied only to `"Imputasi internal per basis"` columns, same all-other-columns-untouched contract as the baseline functions.
- `scripts/run_missforest_imputation.py` — CLI producing `data_processed/tkpi_imputed_missforest.csv` / `myfcd_imputed_missforest.csv`.

**Definition of Done:** script runs end-to-end; zero missing values in targeted columns; reproducible given fixed `RANDOM_SEED`.

**Semantic Commit:** `feat(missforest): add within-database MissForest imputation`

**Claude Code Prompt:**
```
Objective: Implement within-database MissForest imputation (the project's
primary ML method per its research objective), fit and applied separately
for TKPI and MyFCD — no cross-database transfer in this milestone.

Repository context: food-nutrition repo, Stage 3 in progress. Milestone 1
chose and installed a MissForest-capable dependency (check requirements.txt
and its accompanying commit message/body for which package and why — either
`missingpy` or a hand-built
IterativeImputer(estimator=RandomForestRegressor) approach). Baselines
(mean/median/knn/mice) already exist in src/imputation/baselines.py and
scripts/run_baseline_imputation.py as a style reference.

Read these files first:
- requirements.txt and the git log/commit body of Milestone 1's commit
  (chore(config): add imputation dependencies and Stage 3 configuration
  scaffold) to confirm exactly which MissForest package/approach was chosen
- src/imputation/baselines.py (mirror its function signature style: takes
  df and columns, returns a copy with only those columns changed)
- src/imputation/io_utils.py (load_enriched, get_strategy,
  validate_imputed_output, write_output)
- scripts/run_baseline_imputation.py (mirror its argparse/main() structure
  and "[IMPUTE] ..." print style)
- config/imputation_settings.py (RANDOM_SEED, and add missforest output path
  constants here if not already present from Milestone 1)

Reuse these utilities:
- src.imputation.io_utils (all functions)
- config.imputation_settings.RANDOM_SEED
- The same "Imputasi internal per basis" column-selection approach used in
  Milestones 3-5 (extract to a shared helper in io_utils.py ONLY if it is
  not already there — if it's still duplicated per-script, leave it as-is
  and note in the commit body that consolidating it is a candidate follow-up,
  do not refactor other milestones' scripts as a side effect of this one)

Modify only:
- Create src/imputation/missforest_imputer.py
- Create scripts/run_missforest_imputation.py

Do not touch:
- src/imputation/baselines.py, src/imputation/io_utils.py
- Any existing baseline output files or scripts

Expected implementation boundaries:
- src/imputation/missforest_imputer.py:
  missforest_impute(df: pd.DataFrame, columns: list[str],
  random_state: int | None = None) -> pd.DataFrame — fits MissForest
  (via whichever package Milestone 1 selected) restricted to `columns`,
  defaulting random_state to config.imputation_settings.RANDOM_SEED when
  None; same all-other-columns-pass-through contract as the baseline
  functions; this function must NOT mix TKPI and MyFCD rows — it is called
  once per source by the script, each time on that source's own DataFrame
  only.
- scripts/run_missforest_imputation.py: same CLI/main() shape as
  scripts/run_baseline_imputation.py but simpler (MissForest is one method,
  not four) — no --method flag needed unless you want a --within-only flag
  to distinguish this from Milestone 7's cross-transfer script (Milestone 7
  will be a separate script, so this one only ever does within-database).
  For each source in ["TKPI", "MyFCD"]: load via io_utils.load_enriched,
  determine target columns via io_utils.get_strategy filtered to
  "Imputasi internal per basis", run missforest_impute, validate via
  io_utils.validate_imputed_output, write to
  data_processed/tkpi_imputed_missforest.csv /
  data_processed/myfcd_imputed_missforest.csv via io_utils.write_output.

Expected outputs: data_processed/tkpi_imputed_missforest.csv,
data_processed/myfcd_imputed_missforest.csv.

Validation requirements: Run the script; confirm both output files have
zero missing values in targeted columns via io_utils.validate_imputed_output
(already wired into the script); run twice and confirm reproducibility given
the fixed seed.

Testing requirements: Do not add tests yet (Milestone 10). Confirm existing
pytest suite still passes.

Documentation requirements: Docstring on missforest_impute explaining the
within-database (no transfer) scope and pointing readers to Milestone 7's
module for the cross-database variant.

Logging requirements: "[IMPUTE] ..." print style consistent with prior
milestones.

Coding standards: PEP8, type hints, no hardcoded paths, random seed control
via config, no duplicated logic versus baselines.py/io_utils.py.

Definition of Done: script runs end-to-end for both sources with zero
remaining missing values in targeted columns; reproducible; existing pytest
suite green; baselines.py and io_utils.py provably unchanged.

What must NOT be changed: src/imputation/baselines.py,
src/imputation/io_utils.py, existing baseline output files.

End with one commit:
feat(missforest): add within-database MissForest imputation
```

---

## Milestone 7 — Cross-database MissForest transfer (TKPI → MyFCD)

**Purpose:** The project's stated methodological novelty (README: *"MissForest dengan pendekatan cross-database transfer (imputer dilatih pada TKPI, diterapkan pada MyFCD)"*) — for nutrients where MyFCD has 0% availability but TKPI has non-trivial availability (per `availability_matrix.csv`'s `"Cross-DB transfer / USDA"` strategy), fit the imputer on TKPI and apply it to fill the corresponding MyFCD columns.

**Existing files to inspect:**
- `src/imputation/missforest_imputer.py` (Milestone 6 — reuse its underlying fit/transform logic, don't reimplement a parallel random-forest imputer from scratch)
- `data_processed/availability_matrix.csv` (nutrients with strategy `"Cross-DB transfer / USDA"`, e.g. `carotene_total_mcg`)
- `data_processed/tkpi_myfcd_links_mutual.csv` (the 52 mutual-best TKPI↔MyFCD row pairs — the only rows with a reliable cross-source correspondence)
- README section "Metodologi Sub-Riset" point 3, for the intended semantics of "cross-database transfer" (train on TKPI's fuller distribution, apply the fitted relationship to MyFCD, since MyFCD lacks the signal to impute those columns from its own data at all — this is a schema-level transfer using the shared 22-column feature space, not a row-by-row join; the mutual-links table is available for anyone who wants to validate the transfer against the 52 known-correspondence pairs, e.g. in Stage 4 evaluation, but is not required to perform the transfer itself since both datasets share the same column schema)

**Files to modify:**
- Create `src/imputation/cross_transfer.py`
- Create `scripts/run_missforest_imputation.py` — **extend, don't recreate** (add a `--cross-db` flag or a second function call in `main()`, per Milestone 6's existing script)

**Files forbidden to touch:** `src/imputation/missforest_imputer.py`'s existing within-database function; `src/imputation/io_utils.py`.

**Deliverables:**
- `cross_db_transfer_impute(train_df, apply_df, columns, random_state=None) -> pd.DataFrame` in `src/imputation/cross_transfer.py` — fits a MissForest-style estimator on `train_df` (TKPI, which has real values in `columns`) using the full shared feature space (all `NUTRIENT_FIELDS`, using TKPI's own already-available values as predictors), then applies the fitted model to predict `columns` for `apply_df` (MyFCD) rows.
- `scripts/run_missforest_imputation.py` updated to also run the cross-DB step for the `"Cross-DB transfer / USDA"` nutrients and write `data_processed/myfcd_imputed_crossdb.csv`.

**Definition of Done:** `myfcd_imputed_crossdb.csv` has values (not NaN) in every nutrient whose strategy is `"Cross-DB transfer / USDA"`, for every MyFCD row; TKPI is not modified by this milestone (it is the training source, not a transfer target).

**Semantic Commit:** `feat(missforest): add cross-database MissForest transfer (TKPI to MyFCD)`

**Claude Code Prompt:**
```
Objective: Implement the project's headline methodological contribution —
cross-database MissForest transfer, where an imputer is trained on TKPI
(which has partial real data for certain nutrients) and applied to fill
those same nutrients in MyFCD (which has 0% availability for them).

Repository context: food-nutrition repo, Stage 3 in progress. Milestone 6
added src/imputation/missforest_imputer.py with a within-database
missforest_impute(df, columns, random_state) function and
scripts/run_missforest_imputation.py that currently only does within-database
imputation for both sources. This milestone adds the cross-database variant
and wires it into the same script.

Read these files first:
- src/imputation/missforest_imputer.py (reuse its underlying estimator
  choice/fitting approach — do not introduce a second, different random
  forest imputation implementation; if missforest_impute's internals aren't
  easily reusable as a train-on-X-apply-to-Y function, refactor
  missforest_imputer.py minimally to expose a lower-level fit/apply function
  that both the within-database and cross-database paths can call, and
  explain that refactor in the commit body)
- scripts/run_missforest_imputation.py (extend this file's main(), do not
  create a competing script)
- data_processed/availability_matrix.csv (identify exactly which nutrients
  have strategi_imputasi == "Cross-DB transfer / USDA" — this milestone only
  ever touches those columns)
- data_processed/tkpi_myfcd_links_mutual.csv (available for reference/future
  evaluation use, but not required for the transfer itself — the transfer
  operates on the shared 22-column feature schema, not on row-level pairs;
  read the README's "Metodologi Sub-Riset" section 3 for the intended
  semantics before implementing)
- src/schema/nutrition_schema.py (NUTRIENT_FIELDS — the shared feature space
  both TKPI and MyFCD are expressed in)
- README.md section "## Metodologi Sub-Riset (Harmonisasi & Integrasi)",
  point 3, for the documented intent of this method

Reuse these utilities:
- src.imputation.io_utils (load_enriched, get_strategy,
  validate_imputed_output, write_output)
- config.imputation_settings.RANDOM_SEED
- src.imputation.missforest_imputer's underlying fitting logic (do not
  duplicate a second random-forest-imputation implementation)

Modify only:
- Create src/imputation/cross_transfer.py
- Extend scripts/run_missforest_imputation.py (add the cross-DB step; do not
  rewrite the within-database logic already there from Milestone 6)
- src/imputation/missforest_imputer.py MAY be refactored minimally (e.g.
  extracting a shared fit/apply helper) ONLY if strictly necessary to avoid
  duplicating the random-forest-imputation implementation — if you do this,
  the within-database missforest_impute's external behavior and signature
  must remain unchanged; document the refactor explicitly in the commit body

Do not touch:
- src/imputation/io_utils.py
- src/imputation/baselines.py
- data_processed/tkpi_imputed_missforest.csv,
  myfcd_imputed_missforest.csv (Milestone 6's outputs — untouched by this
  milestone)
- data_processed/tkpi_myfcd_links_mutual.csv (read-only)

Expected implementation boundaries:
- src/imputation/cross_transfer.py:
  cross_db_transfer_impute(train_df: pd.DataFrame, apply_df: pd.DataFrame,
  columns: list[str], random_state: int | None = None) -> pd.DataFrame —
  fits an imputation model on train_df (TKPI) using the shared
  NUTRIENT_FIELDS feature space (predictors = all nutrient columns TKPI has
  reasonable availability for, target = each column in `columns`), then
  applies that fitted model's predict step to apply_df (MyFCD) to fill
  `columns` there; returns a copy of apply_df with only `columns` replaced,
  all other apply_df columns unchanged; must not modify or return train_df;
  default random_state to config.imputation_settings.RANDOM_SEED.
  Document clearly in the docstring that TKPI is never modified by this
  function — it is purely the training source.
- scripts/run_missforest_imputation.py: after the existing within-database
  loop, add a step that: loads TKPI and MyFCD via io_utils.load_enriched,
  determines cross-DB target columns via io_utils.get_strategy filtered to
  "Cross-DB transfer / USDA", calls cross_db_transfer_impute(train_df=TKPI,
  apply_df=MyFCD, columns=...), validates the MyFCD result via
  io_utils.validate_imputed_output, and writes
  data_processed/myfcd_imputed_crossdb.csv via io_utils.write_output. Add a
  corresponding path constant to config/imputation_settings.py if one
  doesn't already exist (ADD, don't rename Milestone 6's constants).

Expected outputs: data_processed/myfcd_imputed_crossdb.csv only (no TKPI
output from this milestone).

Validation requirements: Confirm every nutrient with strategy
"Cross-DB transfer / USDA" (e.g. carotene_total_mcg) has zero remaining
missing values in myfcd_imputed_crossdb.csv, via
io_utils.validate_imputed_output; confirm TKPI's enriched input file is
byte-identical before and after running the script (it must not be
modified).

Testing requirements: Do not add tests yet (Milestone 10). Confirm existing
pytest suite still passes.

Documentation requirements: Docstring on cross_db_transfer_impute explaining
the train-on-TKPI/apply-to-MyFCD direction and why (MyFCD has 0% real data
for these nutrients per availability_matrix.csv, so within-database
imputation is impossible for them).

Logging requirements: "[IMPUTE] ..." print style consistent with prior
milestones.

Coding standards: PEP8, type hints, no hardcoded paths, random seed control,
no duplicated random-forest-imputation implementation between
missforest_imputer.py and cross_transfer.py.

Definition of Done: myfcd_imputed_crossdb.csv has zero missing values in the
targeted cross-DB nutrients; TKPI enriched input is unmodified; existing
pytest suite green; Milestone 6's within-database function signature and
behavior are unchanged (or, if refactored for reuse, behaviorally
equivalent and explicitly documented as such).

What must NOT be changed: src/imputation/io_utils.py,
src/imputation/baselines.py, tkpi_myfcd_links_mutual.csv, the within-database
outputs from Milestone 6.

End with one commit:
feat(missforest): add cross-database MissForest transfer (TKPI to MyFCD)
```

---

## Milestone 8 — USDA value-borrowing pass-through + integrated dataset assembly

**Purpose:** Assemble one final "best value per nutrient per food" dataset per the `availability_matrix.csv` routing: nutrients with `"Imputasi internal per basis"` come from the chosen best-performing baseline/MissForest output (Stage 4 will determine "best" — for Stage 3's purposes, default to the within-database MissForest result, since it is the project's primary method, with baselines retained separately for comparison), nutrients with `"Cross-DB transfer / USDA"` come from `myfcd_imputed_crossdb.csv` (MyFCD side) plus TKPI's own internally-imputed value (TKPI side, since TKPI already has partial real data there), and nutrients with `"Pinjam USDA (kosong di kedua basis)"` are filled from the already-present USDA-borrowed columns in `tkpi_enriched.csv`/`myfcd_enriched.csv` (e.g. `vitamin_a_mcg` has no analogue there today — flag it clearly as still-missing/unresolved rather than fabricating a value, since the enriched files' 6 borrowed columns are `magnesium_mg, sugars_total_g, saturated_fat_g, cholesterol_mg, vitamin_b6_mg, vitamin_b12_mcg`, which do not include `vitamin_a_mcg` itself).

**Existing files to inspect:**
- All prior Stage 3 outputs (`tkpi_imputed_baseline_*.csv`, `myfcd_imputed_baseline_*.csv`, `tkpi_imputed_missforest.csv`, `myfcd_imputed_missforest.csv`, `myfcd_imputed_crossdb.csv`)
- `data_processed/tkpi_enriched.csv`, `myfcd_enriched.csv` (for the already-present USDA-borrowed columns)
- `data_processed/availability_matrix.csv`
- `scripts/build_repository_sample.py` (for the concat/merge style used to build `nutrition_repository_sample.csv` — mirror this pattern for the imputed equivalent)

**Files to modify:**
- Create `src/imputation/integrate.py`
- Create `scripts/run_integration.py`

**Files forbidden to touch:** any of the per-method output files from Milestones 3–7 (read-only inputs to this milestone).

**Deliverables:**
- `assemble_integrated(tkpi_sources: dict, myfcd_sources: dict) -> pd.DataFrame` — per-nutrient selection logic driven by `availability_matrix.csv`'s `strategi_imputasi` column, documented explicitly with the fallback rule above for nutrients where even the routing table's strategy cannot fully resolve a value (e.g. `vitamin_a_mcg`) — such cells remain `NaN` and are counted/reported, not invented.
- `scripts/run_integration.py` — CLI producing `data_processed/nutrition_repository_imputed.csv` (schema-column-ordered, via `src.schema.nutrition_schema.schema_columns()`) and `reports/imputation_summary.md` (counts of how many nutrient-cells were resolved via each strategy, and how many remain unresolved).

**Definition of Done:** `nutrition_repository_imputed.csv` exists with 1,380 rows (1,146 TKPI + 234 MyFCD, matching `integration_summary.md`'s existing totals); `reports/imputation_summary.md` accounts for 100% of nutrient-cells across one of: resolved-internal, resolved-cross-db, resolved-usda-borrow, or still-unresolved (no silent gaps).

**Semantic Commit:** `feat(imputation): assemble integrated dataset from all Stage 3 methods per availability-matrix routing`

**Claude Code Prompt:**
```
Objective: Assemble the final "best available value per nutrient per food"
integrated dataset, combining outputs from all prior Stage 3 methods
according to the routing already established in
data_processed/availability_matrix.csv, and produce a summary report
accounting for every nutrient-cell's resolution status.

Repository context: food-nutrition repo, Stage 3 nearly complete. Available
inputs from prior milestones: data_processed/tkpi_imputed_baseline_{mean,
median,knn,mice}.csv, myfcd_imputed_baseline_{mean,median,knn,mice}.csv,
tkpi_imputed_missforest.csv, myfcd_imputed_missforest.csv,
myfcd_imputed_crossdb.csv. Also available: data_processed/tkpi_enriched.csv,
myfcd_enriched.csv (containing 6 already-borrowed USDA columns:
magnesium_mg, sugars_total_g, saturated_fat_g, cholesterol_mg,
vitamin_b6_mg, vitamin_b12_mcg, each with _source/_confidence companions).

Read these files first:
- data_processed/availability_matrix.csv (the routing table — read every
  row; note the three strategy values and which specific nutrients fall
  into each)
- data_processed/tkpi_enriched.csv, myfcd_enriched.csv (header row — confirm
  exactly which 6 nutrients already have USDA-borrowed values, and note that
  vitamin_a_mcg, which has strategy "Pinjam USDA (kosong di kedua basis)" in
  the availability matrix, is NOT among the 6 already-borrowed columns —
  this is a real, currently-unresolved gap that must be surfaced, not
  papered over)
- scripts/build_repository_sample.py (mirror its column-ordering-via-
  schema_columns() pattern and its report-writing style for
  reports/integration_summary.md, adapted to reports/imputation_summary.md)
- src/schema/nutrition_schema.py (schema_columns(), NUTRIENT_FIELDS)
- All of src/imputation/io_utils.py, baselines.py, missforest_imputer.py,
  cross_transfer.py (understand exactly what each prior milestone produced
  and where)

Reuse these utilities:
- src.imputation.io_utils.write_output
- src.schema.nutrition_schema.schema_columns()
- The read-CSV/guard-missing-file style from
  scripts/build_repository_sample.py's load_clean

Modify only:
- Create src/imputation/integrate.py
- Create scripts/run_integration.py

Do not touch:
- Any file produced by Milestones 3-7 (read-only inputs)
- data_processed/tkpi_enriched.csv, myfcd_enriched.csv,
  availability_matrix.csv
- data_processed/nutrition_repository_sample.csv (the ORIGINAL, pre-
  imputation merged file from the existing pipeline — this milestone
  produces a NEW, separate file, nutrition_repository_imputed.csv; it must
  not overwrite or modify the original sample file)

Expected implementation boundaries:
- src/imputation/integrate.py:
  assemble_integrated(tkpi_sources: dict[str, pd.DataFrame],
  myfcd_sources: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, dict] —
  tkpi_sources/myfcd_sources are dicts keyed by a method name (e.g.
  "missforest", "baseline_mean", "enriched") mapping to the corresponding
  loaded DataFrame. For each nutrient in NUTRIENT_FIELDS, look up its
  strategy via the availability matrix and select the source value as
  follows: "Imputasi internal per basis" -> take the value from the
  "missforest" source (Milestone 6's within-database output) for that
  source's own dataset; "Cross-DB transfer / USDA" -> for MyFCD rows, take
  the value from the "crossdb" source (Milestone 7's output); for TKPI rows,
  take the value from the "missforest" (within-database) source, since TKPI
  has partial real+imputed data for these nutrients already; "Pinjam USDA
  (kosong di kedua basis)" -> take the value from the "enriched" source's
  matching USDA-borrowed column IF that nutrient is one of the 6 already-
  borrowed columns (magnesium_mg, sugars_total_g, saturated_fat_g,
  cholesterol_mg, vitamin_b6_mg, vitamin_b12_mcg); OTHERWISE (e.g.
  vitamin_a_mcg) leave the value as NaN and record it in the returned stats
  dict as unresolved — do not fabricate a value. Return both the assembled
  DataFrame (all schema_columns(), in that order, for all TKPI+MyFCD rows
  concatenated) and a stats dict counting resolved-internal,
  resolved-crossdb, resolved-usda-borrow, and unresolved cell counts per
  nutrient.
- scripts/run_integration.py: loads every required input file (with clear
  errors if any prior-milestone output is missing — this script cannot
  silently proceed with a subset), calls assemble_integrated, writes the
  result to data_processed/nutrition_repository_imputed.csv via
  io_utils.write_output (columns ordered via schema_columns()), and writes
  reports/imputation_summary.md summarizing the stats dict in a
  markdown table (nutrient | strategy | resolved_count | unresolved_count),
  matching the "# Heading" + bullet/table style of existing reports/*.md
  files.

Expected outputs: data_processed/nutrition_repository_imputed.csv,
reports/imputation_summary.md.

Validation requirements: Confirm nutrition_repository_imputed.csv has 1380
total rows (1146 TKPI + 234 MyFCD), matching the row counts already
documented in reports/integration_summary.md; confirm reports/
imputation_summary.md's resolved+unresolved counts sum to total_rows ×
len(NUTRIENT_FIELDS) for every nutrient (full accounting, no silent gaps);
confirm vitamin_a_mcg is explicitly reported as unresolved rather than
silently filled or silently dropped from the report.

Testing requirements: Do not add tests yet (Milestone 10). Confirm existing
pytest suite still passes.

Documentation requirements: Docstring on assemble_integrated explaining the
per-strategy source-selection rules above, including the explicit
non-fabrication policy for nutrients like vitamin_a_mcg.

Logging requirements: "[IMPUTE] ..." print style consistent with prior
milestones.

Coding standards: PEP8, type hints, no hardcoded paths, no silent data
fabrication, full accounting of resolved vs. unresolved cells.

Definition of Done: integrated CSV and summary report are produced with
correct row counts and full cell-level accounting; existing pytest suite
green; no prior milestone's output files are modified.

What must NOT be changed: any file from Milestones 1-7,
data_processed/nutrition_repository_sample.csv (the original, distinct from
this milestone's nutrition_repository_imputed.csv),
data_processed/tkpi_enriched.csv, myfcd_enriched.csv, availability_matrix.csv.

End with one commit:
feat(imputation): assemble integrated dataset from all Stage 3 methods per availability-matrix routing
```

---

## Milestone 9 — Evaluation-ready long-format export

**Purpose:** Produce the artifact Stage 4 (Fetty, out of scope for you) actually needs: a long-format table with one row per (food, nutrient, method) so Stage 4 can compare mean/median/KNN/MICE/MissForest/cross-DB against each other and against held-out real values, without Stage 3 having to know anything about Stage 4's evaluation metrics itself.

**Existing files to inspect:**
- All Milestone 3–8 outputs
- `reports/imputation_summary.md` (Milestone 8, for consistent reporting style)
- `data_processed/nutrition_repository_sample.csv` (original, real, non-imputed values — needed so Stage 4 can eventually compute error metrics against ground truth for cells that were originally present but could be held out; Stage 3 only needs to make the real values available in long format alongside imputed ones, not compute any accuracy metric itself, which is explicitly Stage 4's job)

**Files to modify:**
- Create `src/imputation/evaluation_export.py`
- Create/extend `scripts/run_integration.py` (add the long-format export step) **or** a new `scripts/export_evaluation_ready.py` — **decision for this roadmap: separate script**, since it's a distinct output concern from the wide-format integration in Milestone 8, and Stage 4 should be able to regenerate its input without re-running the full integration if only the export logic changes.

**Files forbidden to touch:** Milestone 8's `integrate.py`/`run_integration.py`.

**Deliverables:**
- `to_long_format(sources: dict[str, pd.DataFrame], value_columns: list[str]) -> pd.DataFrame` in `evaluation_export.py` — output columns: `food_id, source_db, nutrient, method, value`.
- `scripts/export_evaluation_ready.py` — CLI producing `data_processed/nutrition_repository_imputed_long.csv` and `reports/imputation_method_comparison.csv` (one row per nutrient × method, with basic descriptive stats — mean/std of imputed values per method — explicitly labeled as descriptive only, NOT an accuracy comparison, since ground-truth-based accuracy comparison is Stage 4's responsibility).

**Definition of Done:** long-format CSV contains rows for every method produced by Milestones 3–8 (mean, median, knn, mice, missforest, crossdb, usda_borrow, original) for every applicable nutrient/food; `imputation_method_comparison.csv` has no NaN in its descriptive-stat columns for any method that actually ran.

**Semantic Commit:** `feat(imputation): add evaluation-ready long-format export for Stage 4`

**Claude Code Prompt:**
```
Objective: Produce a long-format, evaluation-ready export combining every
Stage 3 imputation method's output, for Stage 4 (evaluation, owned by a
different team member) to consume. This milestone does NOT compute any
accuracy/error metric against ground truth — that is explicitly Stage 4's
responsibility. It only reshapes and exposes the data.

Repository context: food-nutrition repo, Stage 3 nearly complete. Available
inputs: data_processed/tkpi_imputed_baseline_{mean,median,knn,mice}.csv,
myfcd_imputed_baseline_{mean,median,knn,mice}.csv,
tkpi_imputed_missforest.csv, myfcd_imputed_missforest.csv,
myfcd_imputed_crossdb.csv, data_processed/nutrition_repository_imputed.csv
(Milestone 8's integrated output), data_processed/nutrition_repository_sample.csv
(original real values, pre-imputation).

Read these files first:
- src/imputation/integrate.py, scripts/run_integration.py (Milestone 8 —
  understand its source-selection logic and output schema; do not modify
  either file)
- reports/imputation_summary.md (Milestone 8's report — match its markdown
  table style for the new comparison report)
- data_processed/nutrition_repository_sample.csv (the ORIGINAL merged file,
  with real un-imputed values, still containing NaN/missing for cells that
  were never filled by the original scrape-clean-merge pipeline)
- src/schema/nutrition_schema.py (NUTRIENT_FIELDS)

Reuse these utilities:
- src.imputation.io_utils.write_output
- src.schema.nutrition_schema.NUTRIENT_FIELDS

Modify only:
- Create src/imputation/evaluation_export.py
- Create scripts/export_evaluation_ready.py

Do not touch:
- src/imputation/integrate.py, scripts/run_integration.py
- Any Milestone 3-8 output file (read-only inputs)
- data_processed/nutrition_repository_sample.csv (read-only input)

Expected implementation boundaries:
- src/imputation/evaluation_export.py:
  to_long_format(sources: dict[str, pd.DataFrame], value_columns: list[str])
  -> pd.DataFrame — sources is a dict keyed by method name (e.g. "mean",
  "median", "knn", "mice", "missforest", "crossdb", "original") mapping to
  that method's DataFrame (must include food_id and source columns from the
  original schema); melts each source's value_columns (the nutrient columns)
  into long format with columns [food_id, source_db, nutrient, method,
  value], then concatenates all methods into one long DataFrame. Must not
  drop rows where value is still NaN (Stage 4 needs to see unresolved cells
  too, e.g. vitamin_a_mcg per Milestone 8's documented gap) — instead, keep
  them and let the row's value be NaN.
- scripts/export_evaluation_ready.py: loads every Milestone 3-8 output file
  plus the original nutrition_repository_sample.csv (as the "original"
  method), calls to_long_format, writes
  data_processed/nutrition_repository_imputed_long.csv via
  io_utils.write_output. Also computes, per (nutrient, method) pair, simple
  descriptive statistics (count of non-null values, mean, std) — NOT any
  accuracy/error metric — and writes them to
  reports/imputation_method_comparison.csv. Clearly label in a header
  comment / report intro line that this is descriptive only and that
  accuracy evaluation against held-out ground truth is Stage 4's
  responsibility, not this script's.

Expected outputs: data_processed/nutrition_repository_imputed_long.csv,
reports/imputation_method_comparison.csv.

Validation requirements: Confirm the long-format CSV contains rows for every
method listed above, for every nutrient in NUTRIENT_FIELDS, for every food
in both sources (i.e. row count = num_foods × num_nutrients × num_methods,
accounting for the fact that not every method necessarily targeted every
nutrient — document any such gaps explicitly rather than silently omitting
combinations); confirm imputation_method_comparison.csv has no NaN in its
count/mean/std columns for any (nutrient, method) pair where that method
actually produced output for that nutrient.

Testing requirements: Do not add tests yet (Milestone 10). Confirm existing
pytest suite still passes.

Documentation requirements: Docstring on to_long_format and a clear
in-report disclaimer (as described above) that this export is descriptive,
not evaluative.

Logging requirements: "[IMPUTE] ..." print style consistent with prior
milestones.

Coding standards: PEP8, type hints, no hardcoded paths, no accuracy/error
computation (explicitly out of Stage 3 scope, reserved for Stage 4).

Definition of Done: long-format CSV and comparison report are produced
correctly and completely; existing pytest suite green; no Milestone 3-8
file is modified.

What must NOT be changed: src/imputation/integrate.py,
scripts/run_integration.py, any Milestone 3-8 output file,
data_processed/nutrition_repository_sample.csv.

End with one commit:
feat(imputation): add evaluation-ready long-format export for Stage 4
```

---

## Milestone 10 — Unit tests for all Stage 3 modules

**Purpose:** Bring Stage 3 up to the same test-coverage discipline already established for `src/cleaning`, `src/schema`, and `src/validation` (pytest + small CSV fixtures), and add explicit reproducibility checks (random-seed control) that no prior milestone was required to formalize as an automated test.

**Existing files to inspect:**
- `tests/test_normalizers.py`, `test_quality_checks.py`, `test_schema.py` (style/structure to mirror exactly)
- `tests/fixtures/sample_fixture_tkpi.csv`, `sample_fixture_myfcd.csv` (fixture conventions — note the existing `fixture_label` column pattern that's dropped before use)
- Every `src/imputation/*.py` module from Milestones 2–9

**Files to modify:**
- Create `tests/test_imputation_io.py`, `tests/test_baselines.py`, `tests/test_missforest.py`, `tests/test_integration.py`
- Create `tests/fixtures/sample_fixture_enriched_tkpi.csv`, `sample_fixture_enriched_myfcd.csv` (small, hand-built or subsampled fixtures mirroring the real `*_enriched.csv` schema, small enough to run fast in CI, with deliberately-injected missing values covering all three `availability_matrix.csv` strategies)

**Files forbidden to touch:** any existing test file, any existing fixture file, any `src/imputation/*.py` module (tests must exercise the existing implementation as-is; if a genuine bug is found while writing tests, report it in the commit body rather than silently patching the implementation in the same commit).

**Deliverables:**
- Tests for `io_utils.get_strategy` (correct routing for all three strategies, `KeyError` for unknown nutrients), `mean_impute`/`median_impute`/`knn_impute`/`mice_impute` (correctness on the small fixture, non-targeted columns untouched, reproducibility for `mice_impute` given fixed seed), `missforest_impute` and `cross_db_transfer_impute` (zero missing values in targeted columns post-imputation on the fixture, TKPI-fixture unmodified by the cross-transfer test), and `assemble_integrated` (correct strategy-based source selection, explicit unresolved-cell handling for a fixture nutrient with no USDA-borrow column available).

**Definition of Done:** `pytest` passes with 100% of new tests green, and the full existing suite (`test_normalizers.py`, `test_quality_checks.py`, `test_schema.py`, plus the four new files) is green together.

**Semantic Commit:** `test(imputation): add unit tests and fixtures for all Stage 3 modules`

**Claude Code Prompt:**
```
Objective: Add pytest unit tests for every src/imputation module built in
Milestones 2-9, following the repository's existing test conventions
exactly, including small hand-built fixtures and explicit reproducibility
checks.

Repository context: food-nutrition repo, Stage 3 functionally complete
(Milestones 1-9 done). No imputation tests exist yet. Existing tests
(tests/test_normalizers.py, test_quality_checks.py, test_schema.py) use
pytest, import directly from src.*, and load small CSV fixtures from
tests/fixtures/.

Read these files first:
- tests/test_normalizers.py, tests/test_quality_checks.py,
  tests/test_schema.py (mirror their import style, function-naming style
  `test_<module>_<behavior>`, and assertion style exactly)
- tests/fixtures/sample_fixture_tkpi.csv, sample_fixture_myfcd.csv (note the
  `fixture_label` column that existing tests drop before use — decide
  whether your new fixtures need the same column for consistency, and
  document your choice)
- Every file under src/imputation/ (io_utils.py, baselines.py,
  missforest_imputer.py, cross_transfer.py, integrate.py,
  evaluation_export.py) — read the actual current implementation, since
  this prompt cannot know every detail Claude Code chose during Milestones
  1-9 (e.g. exact MissForest package, exact config constant names)
- config/imputation_settings.py (RANDOM_SEED and path constants)
- data_processed/availability_matrix.csv (to build a fixture-scale version
  covering all three strategy types)

Reuse these utilities:
- Nothing new — this milestone imports and tests existing code, it does not
  add new production utilities

Modify only:
- Create tests/test_imputation_io.py
- Create tests/test_baselines.py
- Create tests/test_missforest.py
- Create tests/test_integration.py
- Create tests/fixtures/sample_fixture_enriched_tkpi.csv
- Create tests/fixtures/sample_fixture_enriched_myfcd.csv
- Create a small fixture-scale availability matrix if the real one is
  impractical to use directly in fast unit tests (e.g.
  tests/fixtures/sample_fixture_availability_matrix.csv) — only if needed;
  prefer reusing the real data_processed/availability_matrix.csv directly if
  it is fast enough and doesn't make tests fragile to future Stage 2 changes

Do not touch:
- Any existing test file (test_normalizers.py, test_quality_checks.py,
  test_schema.py)
- Any existing fixture file
- Any file under src/imputation/ — if you discover what looks like a bug
  while writing a test, do NOT fix it in this commit; instead write the test
  to document the actual (possibly buggy) current behavior if that's what's
  needed to keep the suite green, and describe the suspected bug clearly in
  the commit message body so it can be triaged separately
- Any file under config/, data_processed/, reports/

Expected implementation boundaries:
- tests/fixtures/sample_fixture_enriched_tkpi.csv and
  sample_fixture_enriched_myfcd.csv: small (roughly 10-20 rows each),
  hand-built or subsampled from the real enriched files, matching their
  exact column schema (22 base nutrients + 6 USDA-borrowed columns with
  _source/_confidence), with deliberately-placed missing values so that at
  least one nutrient in the fixture exercises each of the three
  availability-matrix strategies.
- tests/test_imputation_io.py: tests for load_enriched (happy path + missing
  file), get_strategy (all three strategies + KeyError for an unknown
  nutrient), load_mutual_links, validate_imputed_output (detects remaining
  missing values correctly).
- tests/test_baselines.py: tests for mean_impute, median_impute, knn_impute,
  mice_impute — correctness on the fixture (known small dataset with a
  computable expected mean/median), confirms non-targeted columns are
  unchanged, confirms mice_impute is reproducible (two runs with the same
  seed produce identical output) per the RANDOM_SEED config.
- tests/test_missforest.py: tests for missforest_impute (zero missing values
  in targeted fixture columns after imputation) and
  cross_db_transfer_impute (zero missing values in the MyFCD-fixture target
  columns; TKPI-fixture DataFrame is unchanged/not mutated by the call —
  assert this explicitly, e.g. by comparing to a pre-call copy).
- tests/test_integration.py: tests for assemble_integrated — given the small
  fixtures plus mocked/fixture-scale per-method outputs, confirm the correct
  source is selected per the availability-matrix strategy for at least one
  nutrient of each strategy type, and confirm a nutrient with no available
  USDA-borrow column (mirroring the real vitamin_a_mcg gap) is reported as
  unresolved rather than silently filled.

Expected outputs: the six new files listed above. No production code files
are modified.

Validation requirements: `pytest` run from repo root passes with all new
tests green.

Testing requirements: This milestone IS the testing requirement. Coverage
should touch every public function in src/imputation/*.py at least once.

Documentation requirements: Each test file should have a short module
docstring stating which src/imputation module it covers, matching the
implicit convention of the existing test files (which don't have explicit
docstrings but are clearly one-file-per-module).

Logging requirements: None (tests don't need print-based stage logging).

Coding standards: PEP8, type hints where the existing test files use them
(they currently don't consistently — match whatever the majority pattern in
test_quality_checks.py/test_schema.py is), pytest idioms (plain
`def test_...():` functions, `pytest.raises` for exceptions), no
duplicated fixture-loading boilerplate beyond what the existing test files
already duplicate (mirror their style, don't over-engineer a new fixture
framework).

Definition of Done: full pytest suite (existing three files + four new
files) passes 100% green; every public function added in Milestones 2-9 has
at least one direct test.

What must NOT be changed: any existing test/fixture file, any file under
src/imputation/, config/, data_processed/, reports/.

End with one commit:
test(imputation): add unit tests and fixtures for all Stage 3 modules
```

---

## Milestone 11 — Documentation and optional pipeline wiring

**Purpose:** Document Stage 3 for the rest of the research team (matching the existing `docs/*.md` narrative style) and, only as an additive/opt-in change, make Stage 3 discoverable from `scripts/run_pipeline.py` without altering its existing default behavior.

**Existing files to inspect:**
- `README.md` (structure/tone to match — Bahasa Indonesia narrative style, consistent with existing sections)
- `docs/how_to_run.md`, `docs/progress_report.md`, `docs/final_output_summary.md`
- `scripts/run_pipeline.py` (existing stage list and `--skip-scrape` flag pattern)
- Every `src/imputation/*.py` and `scripts/run_*imputation*.py` / `scripts/run_integration.py` / `scripts/export_evaluation_ready.py` file from Milestones 1–10

**Files to modify:**
- Create `docs/stage3_imputation.md`
- `README.md` (append a new "Stage 3 — Machine Learning Imputation" section; do not rewrite existing sections)
- `scripts/run_pipeline.py` (add new stages **only** behind a new opt-in flag, e.g. `--include-imputation`, defaulting to off, so existing invocations documented in `docs/how_to_run.md` keep working unchanged)

**Files forbidden to touch:** any other `docs/*.md` file; any `src/` or `scripts/` file other than `run_pipeline.py`.

**Deliverables:**
- `docs/stage3_imputation.md` — methodology write-up (mirroring the README's existing "Metodologi Sub-Riset" section style): what each method does, why cross-database transfer was needed for certain nutrients, the explicit `vitamin_a_mcg`-style unresolved-cell caveat, pointers to every output file and report.
- README.md Stage 3 section, and an updated "Output Utama"-style list including the new Stage 3 files.
- `scripts/run_pipeline.py --include-imputation` runs baseline → missforest → integration → evaluation-export as additional stages, appended after the existing `export_repository_json` stage, using the same `run_stage()` helper already defined in that file.

**Definition of Done:** `python scripts/run_pipeline.py --skip-scrape` (no new flag) behaves identically to before this milestone; `python scripts/run_pipeline.py --skip-scrape --include-imputation` additionally runs and reports on all Stage 3 scripts using the existing `run_stage()`/summary-printing mechanism.

**Semantic Commit:** `docs(stage3): document imputation methodology and wire optional pipeline stage`

**Claude Code Prompt:**
```
Objective: Document Stage 3's methodology and outputs for the wider research
team, and make the Stage 3 pipeline optionally runnable from the existing
scripts/run_pipeline.py orchestrator, without changing that script's default
(no-flag) behavior in any way.

Repository context: food-nutrition repo. Stage 3 (Milestones 1-10) is
functionally complete and tested. This is the final Stage 3 milestone:
documentation and optional orchestration wiring only — no new imputation
logic.

Read these files first:
- README.md (full file — match its Bahasa Indonesia narrative tone,
  heading style, and the structure of its existing "Metodologi Sub-Riset"
  and "Output Utama" sections)
- docs/how_to_run.md, docs/progress_report.md, docs/final_output_summary.md
  (existing docs/ style)
- scripts/run_pipeline.py (the existing run_stage() helper, stages list,
  argparse setup with --skip-scrape and --limit, and the final summary-
  printing loop — your new flag and stages must use this exact same
  mechanism, not a parallel one)
- Every src/imputation/*.py file and every scripts/run_*.py /
  scripts/export_*.py file produced in Milestones 1-10 (to accurately
  document what actually exists, not what was originally planned — some
  details, like the exact MissForest package chosen in Milestone 1, are
  only knowable by reading the actual repository state at this point)
- reports/imputation_summary.md and reports/imputation_method_comparison.csv
  (Milestones 8-9 outputs, to reference correctly in the documentation)

Reuse these utilities:
- scripts/run_pipeline.py's existing run_stage(name, command) helper
  function — call it for the new stages, do not write a second
  stage-running mechanism

Modify only:
- Create docs/stage3_imputation.md
- README.md (append only — add a new section; do not edit or remove
  existing sections, do not reorder existing headings)
- scripts/run_pipeline.py (add an --include-imputation flag, default False;
  when True, append baseline/missforest/integration/evaluation-export stages
  to the existing stages list, after export_repository_json; when the flag
  is absent or False, behavior must be byte-for-byte identical to before
  this milestone)

Do not touch:
- Any other file under docs/ (data_dictionary.md, project_scope.md,
  research_context.md, source_recon_report.md, meeting_notes_template.md)
- Any file under src/, or any scripts/*.py file other than run_pipeline.py
- Any data_processed/ or reports/ file

Expected implementation boundaries:
- docs/stage3_imputation.md: sections for each method (mean, median, KNN,
  MICE, within-database MissForest, cross-database MissForest transfer),
  each explaining what it does, which nutrients it targets (per
  availability_matrix.csv's actual strategy assignments), and where its
  output lives; a section explicitly describing the vitamin_a_mcg-style
  unresolved-cell case as a known, documented limitation rather than a bug;
  a table of every new file produced by Stage 3 (data_processed/*, reports/*)
  with a one-line description each; a "How to run" subsection listing the
  exact commands (scripts/run_baseline_imputation.py,
  scripts/run_missforest_imputation.py, scripts/run_integration.py,
  scripts/export_evaluation_ready.py, in that order, plus the combined
  scripts/run_pipeline.py --include-imputation option).
- README.md: one new top-level section, positioned after the existing
  "Output Tahap Resolusi Entitas & Diagnosis Missing Data (Update)" section
  and before "## Temuan Kunci" (or wherever fits the existing document flow
  without disturbing prior content), summarizing Stage 3 at a high level and
  linking to docs/stage3_imputation.md for full detail. Also add the new
  Stage 3 output files to the existing "## Output Utama" list (append, don't
  restructure that list).
- scripts/run_pipeline.py: add `parser.add_argument("--include-imputation",
  action="store_true")`; after the existing stages.extend([...]) call for
  export_repository_json, conditionally extend stages further with the four
  new Stage 3 scripts (only if --include-imputation is set), each added via
  the same `(name, [python, "scripts/...", ...])` tuple shape already used
  for every other stage; do not alter the existing stages list construction,
  the --skip-scrape logic, or the final summary-printing loop.

Expected outputs: docs/stage3_imputation.md (new file), README.md (modified,
append-only), scripts/run_pipeline.py (modified, additive-only under a new
opt-in flag).

Validation requirements: Run `python scripts/run_pipeline.py --skip-scrape`
(no new flag) and confirm its printed stage list and behavior are unchanged
from before this milestone (compare against the stage list documented in
docs/how_to_run.md, which must also still be accurate and is NOT being
edited in this milestone). Then run
`python scripts/run_pipeline.py --skip-scrape --include-imputation` and
confirm the four new stages run and report SUCCESS/FAILED via the existing
run_stage() mechanism.

Testing requirements: Run the full existing pytest suite (including all
Milestone 10 tests) and confirm it is still 100% green — this milestone
should not touch any tested code path in a way that breaks it (argparse
additions to run_pipeline.py are not covered by existing tests, but must
not break anything that is).

Documentation requirements: This milestone IS the documentation
requirement.

Logging requirements: New pipeline stages must use the existing
run_stage()/print(f"[STAGE] ...") mechanism — no new logging approach.

Coding standards: PEP8, type hints on any new function signature, no
hardcoded paths, README/docs written in the same Bahasa Indonesia narrative
style as the existing document (do not switch to English for the new
sections unless the surrounding document context is already
English-language in that spot).

Definition of Done: default `run_pipeline.py` invocation unchanged;
--include-imputation flag correctly runs and reports on all four Stage 3
scripts; docs/stage3_imputation.md accurately describes the actual
implemented system (verified by reading the real Milestone 1-10 code, not
assumed from this prompt); README.md's existing content is fully intact
with only an appended new section and an appended output-file list;
existing pytest suite green.

What must NOT be changed: any docs/ file other than the new
stage3_imputation.md and the append-only edit to README.md; any src/ file;
any scripts/*.py file other than the additive change to run_pipeline.py;
data_processed/, reports/ contents.

End with one commit:
docs(stage3): document imputation methodology and wire optional pipeline stage
```

---

## Summary

11 milestones, each one feature / one commit, strictly additive to the existing repository:

1. `chore(config)` — dependencies + config scaffold
2. `feat(imputation)` — shared I/O + strategy routing + validation
3. `feat(baseline)` — mean + median
4. `feat(baseline)` — KNN
5. `feat(baseline)` — MICE
6. `feat(missforest)` — within-database MissForest
7. `feat(missforest)` — cross-database MissForest transfer (the project's headline novelty)
8. `feat(imputation)` — integrated dataset assembly
9. `feat(imputation)` — evaluation-ready long-format export
10. `test(imputation)` — full test coverage
11. `docs(stage3)` — documentation + optional pipeline wiring

No milestone touches Stage 1/Stage 2 source or output files, `app/prototype.py`, `usda-csv/`, or any existing `src/scrapers`, `src/cleaning`, `src/validation`, `src/schema` implementation. Every prompt is self-contained and instructs Claude Code to re-read the actual current repository state (since exact details like the Milestone-1-chosen MissForest package can only be confirmed by inspection, not assumed in advance).