from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.validation.quality_checks import combine_quality_reports, validate_dataframe


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    reports = []
    for source_name, path in [
        ("TKPI", ROOT / "data_clean" / "tkpi_clean.csv"),
        ("MyFCD", ROOT / "data_clean" / "myfcd_clean.csv"),
    ]:
        if not path.exists() or path.stat().st_size == 0:
            print(f"[VALIDATE] {source_name}: skipped, clean file not found")
            continue
        try:
            df = pd.read_csv(path)
        except pd.errors.EmptyDataError:
            print(f"[VALIDATE] {source_name}: skipped, clean file empty")
            continue
        reports.append(validate_dataframe(df, source_name))

    combined = combine_quality_reports(reports) if reports else {
        "total_rows": 0,
        "valid_rows": 0,
        "invalid_rows": 0,
        "duplicate_count": 0,
        "issues_by_type": {},
        "warnings_by_type": {},
        "sources": [],
    }

    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "data_quality_report.json").write_text(
        json.dumps(combined, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = ["# Data Quality Report", ""]
    lines.append(f"- Total rows: {combined['total_rows']}")
    lines.append(f"- Valid rows: {combined['valid_rows']}")
    lines.append(f"- Invalid rows: {combined['invalid_rows']}")
    lines.append(f"- Duplicate count: {combined['duplicate_count']}")
    lines.append("")
    lines.append("## Issues by Type")
    if combined["issues_by_type"]:
        for key, value in combined["issues_by_type"].items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- No hard validation issues found.")
    lines.append("")
    lines.append("## Warnings by Type")
    if combined["warnings_by_type"]:
        for key, value in combined["warnings_by_type"].items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- No warnings found.")
    lines.append("")
    lines.append("## Source Detail")
    for report in combined["sources"]:
        lines.append(f"- {report['source']}: {report['valid_rows']}/{report['total_rows']} valid rows")

    (ROOT / "reports" / "data_quality_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[VALIDATE] total_rows={combined['total_rows']} invalid_rows={combined['invalid_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
