"""Pindai seluruh CSV di repo untuk sel angka yang memakai koma.

Melaporkan, per berkas dan per kolom, sel dengan koma ribuan (mis. "3,784",
"1,234.5") dan sel dengan koma desimal (mis. "0,5", "12,05"). Keluar dengan
kode 1 bila ada koma desimal, sehingga bisa dipakai sebagai pemeriksaan CI.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__"}

THOUSANDS_PATTERN = re.compile(r"^[-+]?\d{1,3}(?:,\d{3})+(?:\.\d+)?$")
DECIMAL_COMMA_PATTERN = re.compile(r"^[-+]?\d+,\d+$")


def classify(value: str) -> str | None:
    text = value.strip()
    if "," not in text:
        return None
    if THOUSANDS_PATTERN.match(text):
        return "thousands"
    if DECIMAL_COMMA_PATTERN.match(text):
        return "decimal"
    return None


def iter_csv_files(root: Path):
    for path in sorted(root.rglob("*.csv")):
        if not any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            yield path


def scan_file(path: Path) -> tuple[Counter, Counter, dict[str, str]]:
    thousands: Counter = Counter()
    decimal: Counter = Counter()
    examples: dict[str, str] = {}
    csv.field_size_limit(sys.maxsize)
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        if header is None:
            return thousands, decimal, examples
        for row in reader:
            for index, value in enumerate(row):
                kind = classify(value)
                if kind is None:
                    continue
                column = header[index] if index < len(header) else f"<kolom {index}>"
                (thousands if kind == "thousands" else decimal)[column] += 1
                examples.setdefault(f"{kind}:{column}", value)
    return thousands, decimal, examples


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=ROOT, help="direktori yang dipindai")
    args = parser.parse_args()
    root = args.root.resolve()

    files_with_decimal = 0
    for path in iter_csv_files(root):
        thousands, decimal, examples = scan_file(path)
        if not thousands and not decimal:
            continue
        print(f"{path.relative_to(root)}")
        for label, kind, counts in (("koma desimal", "decimal", decimal), ("koma ribuan", "thousands", thousands)):
            for column, count in counts.most_common():
                print(f"  [{label}] {column}: {count} sel (contoh: {examples[f'{kind}:{column}']!r})")
        if decimal:
            files_with_decimal += 1

    if files_with_decimal:
        print(f"\nGAGAL: koma desimal ditemukan di {files_with_decimal} berkas.")
        return 1
    print("\nOK: tidak ada koma desimal.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
