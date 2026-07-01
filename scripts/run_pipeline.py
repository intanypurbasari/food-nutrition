from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_stage(name: str, command: list[str]) -> dict[str, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode == 0:
        status = "SUCCESS"
    else:
        status = "FAILED"
    message = (result.stdout + result.stderr).strip().splitlines()
    tail = message[-1] if message else ""
    print(f"[STAGE] {name}: {status}" + (f" - {tail}" if tail else ""))
    return {"stage": name, "status": status, "returncode": str(result.returncode), "message": tail}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run nutrition repository pipeline end-to-end.")
    parser.add_argument("--skip-scrape", action="store_true")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    python = sys.executable
    stages: list[tuple[str, list[str]]] = []
    results = []

    if args.skip_scrape and (ROOT / "data_raw" / "tkpi_raw.csv").exists():
        print("[STAGE] tkpi_scrape: SKIPPED - --skip-scrape and raw file exists")
        results.append({"stage": "tkpi_scrape", "status": "SKIPPED", "returncode": "0", "message": "--skip-scrape and raw file exists"})
    else:
        stages.append(("tkpi_scrape", [python, "scripts/scrape_tkpi.py", "--limit", str(args.limit)]))

    if args.skip_scrape and (ROOT / "data_raw" / "myfcd_raw.csv").exists():
        print("[STAGE] myfcd_scrape: SKIPPED - --skip-scrape and raw file exists")
        results.append({"stage": "myfcd_scrape", "status": "SKIPPED", "returncode": "0", "message": "--skip-scrape and raw file exists"})
    else:
        stages.append(("myfcd_scrape", [python, "scripts/scrape_myfcd.py", "--limit", str(args.limit)]))

    stages.extend(
        [
            ("clean_tkpi", [python, "scripts/clean_tkpi.py"]),
            ("clean_myfcd", [python, "scripts/clean_myfcd.py"]),
            ("validate_dataset", [python, "scripts/validate_dataset.py"]),
            ("build_repository_sample", [python, "scripts/build_repository_sample.py"]),
            ("export_repository_json", [python, "scripts/export_repository_json.py"]),
        ]
    )

    for name, command in stages:
        results.append(run_stage(name, command))

    print("\nPipeline summary:")
    for result in results:
        print(f"- {result['stage']}: {result['status']}")
    failures = [result for result in results if result["status"] == "FAILED"]
    if failures:
        print("Pipeline finished with partial failures. See reports/ and logs/ for details.")
    else:
        print("Pipeline finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
