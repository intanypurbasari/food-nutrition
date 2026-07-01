from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.clean_common import ROOT, clean_source


def main() -> int:
    return clean_source(ROOT / "data_raw" / "myfcd_raw.csv", "MyFCD", "myfcd", "myfcd")


if __name__ == "__main__":
    raise SystemExit(main())
