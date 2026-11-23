#!/usr/bin/env python3
"""Compare paired skill-assisted and baseline task outcomes from JSON run records."""
import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

CONDITIONS = {"with_skill", "baseline"}


def load_runs(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    runs = data.get("runs") if isinstance(data, dict) else None
    if not isinstance(runs, list) or not runs:
        raise ValueError("input must be an object with a non-empty runs list")
    seen = set()
    for index, row in enumerate(runs):
        if not isinstance(row, dict):
            raise ValueError(f"runs[{index}] must be an object")
        if not isinstance(row.get("case_id"), str) or not row["case_id"].strip():
            raise ValueError(f"runs[{index}] needs a non-empty case_id")
        if row.get("condition") not in CONDITIONS:
            raise ValueError(f"runs[{index}].condition must be with_skill or baseline")
        if not isinstance(row.get("success"), bool):
            raise ValueError(f"runs[{index}].success must be boolean")
        for field in ("tokens", "duration_ms"):
            if not isinstance(row.get(field), int) or isinstance(row.get(field), bool) or row[field] < 0:
                raise ValueError(f"runs[{index}].{field} must be a non-negative integer")
        key = (row["case_id"], row["condition"], row.get("run_id", index))
        if key in seen:
            raise ValueError(f"duplicate run record for case {row['case_id']} and condition {row['condition']}")
        seen.add(key)
    return runs


def summarize(values):
    return statistics.median(values) if values else None


def compare(runs):
    grouped = defaultdict(lambda: defaultdict(list))
    for row in runs:
        grouped[row["case_id"]][row["condition"]].append(row)
    paired = []
    unpaired = []
    for case_id, conditions in sorted(grouped.items()):
        if not all(conditions.get(name) for name in CONDITIONS):
            unpaired.append(case_id)
            continue
        pairs = {}
        for condition in CONDITIONS:
            rows = conditions[condition]
            pairs[condition] = {"success_rate": sum(x["success"] for x in rows) / len(rows),
                                "median_tokens": summarize([x["tokens"] for x in rows]),
                                "median_duration_ms": summarize([x["duration_ms"] for x in rows]), "runs": len(rows)}
        paired.append({"case_id": case_id, "with_skill": pairs["with_skill"], "baseline": pairs["baseline"],
                       "success_rate_delta": pairs["with_skill"]["success_rate"] - pairs["baseline"]["success_rate"],
                       "median_tokens_delta": pairs["with_skill"]["median_tokens"] - pairs["baseline"]["median_tokens"],
                       "median_duration_ms_delta": pairs["with_skill"]["median_duration_ms"] - pairs["baseline"]["median_duration_ms"]})
    if not paired:
        raise ValueError("at least one case must have runs for both conditions")
    return {"paired_cases": len(paired), "unpaired_cases": unpaired, "cases": paired,
            "summary": {"success_rate_delta_median": summarize([x["success_rate_delta"] for x in paired]),
                        "median_tokens_delta": summarize([x["median_tokens_delta"] for x in paired]),
                        "median_duration_ms_delta": summarize([x["median_duration_ms_delta"] for x in paired])},
            "ok": not unpaired}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", help="JSON file with paired baseline and with_skill run records")
    args = parser.parse_args(argv)
    try:
        result = compare(load_runs(args.runs))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
