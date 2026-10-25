#!/usr/bin/env python3
"""Fail when statement or branch coverage is below its own threshold."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    """Read a coverage JSON report and enforce independent thresholds."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "report",
        nargs="?",
        default="coverage.json",
        type=Path,
        help="coverage.py JSON report (default: coverage.json)",
    )
    parser.add_argument(
        "--min-statements",
        type=float,
        default=95.0,
        help="Minimum statement coverage percentage (default: 92.5)",
    )
    parser.add_argument(
        "--min-branches",
        type=float,
        default=90.0,
        help="Minimum branch coverage percentage (default: 85.0)",
    )
    args = parser.parse_args()

    try:
        data = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Coverage report unavailable: {exc}", file=sys.stderr)
        return 1

    totals = data.get("totals", {})
    try:
        statements = float(totals["percent_statements_covered"])
        branches = float(totals["percent_branches_covered"])
    except (KeyError, TypeError, ValueError) as exc:
        print(f"Coverage report is missing required totals: {exc}", file=sys.stderr)
        return 1

    print(
        f"Statements: {statements:.2f}% (min {args.min_statements:.2f}%) | "
        f"Branches: {branches:.2f}% (min {args.min_branches:.2f}%)"
    )
    failed = False
    if statements < args.min_statements:
        print(
            f"Statement coverage {statements:.2f}% is below {args.min_statements:.2f}%",
            file=sys.stderr,
        )
        failed = True
    if branches < args.min_branches:
        print(
            f"Branch coverage {branches:.2f}% is below {args.min_branches:.2f}%",
            file=sys.stderr,
        )
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
