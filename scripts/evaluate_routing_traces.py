#!/usr/bin/env python3
"""Compare captured skill-read traces to routing seeds; never predicts or routes prompts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEEDS = ROOT / "evals/trigger-routing.json"
DEFAULT_TRACES = ROOT / "evals/captured-read-traces.json"


def _notrun_cases(seeds: list[Any], reason: str) -> list[dict[str, Any]]:
    result = []
    for index, seed in enumerate(seeds):
        case_id = seed.get("id") if isinstance(seed, dict) and isinstance(seed.get("id"), str) else f"invalid-seed-{index}"
        result.append({"case_id": case_id, "status": "NOTRUN", "reason": reason})
    return result


def evaluate_data(seeds: Any, traces: Any, *, trace_error: str | None = None,
                  scope: str = "Captured skill-read traces only; no routing or generation is performed.") -> dict[str, Any]:
    """Positives require expected reads; negatives forbid their primary and permit listed companions."""
    errors: list[str] = []
    if not isinstance(seeds, list) or not seeds:
        return {"status": "NOTRUN", "scope": scope, "summary": {"pass": 0, "fail": 0, "notrun": 0},
                "cases": [], "errors": ["seeds must be a non-empty array"]}
    ids: set[str] = set()
    for index, seed in enumerate(seeds):
        if not isinstance(seed, dict) or not isinstance(seed.get("id"), str) or not seed["id"].strip():
            errors.append(f"seed[{index}]: invalid or missing id")
        elif seed["id"] in ids:
            errors.append(f"seed[{index}]: duplicate id {seed['id']!r}")
        else:
            ids.add(seed["id"])
    if errors:
        cases = _notrun_cases(seeds, "invalid seed catalog")
        return _report(cases, errors, scope)
    if trace_error:
        return _report(_notrun_cases(seeds, trace_error), [trace_error], scope)
    if isinstance(traces, dict):
        traces = traces.get("traces")
    if not isinstance(traces, list):
        return _report(_notrun_cases(seeds, "trace input must be an array"), ["trace input must be an array"], scope)
    if not traces:
        return _report(_notrun_cases(seeds, "trace collection is empty"), ["trace collection is empty"], scope)

    known = {seed["id"]: seed for seed in seeds}
    by_id: dict[str, list[Any]] = {}
    for index, trace in enumerate(traces):
        if not isinstance(trace, dict):
            errors.append(f"trace[{index}]: expected object")
            continue
        case_id = trace.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"trace[{index}]: case_id must be a non-empty string")
            continue
        if case_id not in known:
            errors.append(f"trace[{index}]: unknown case_id {case_id!r}")
            continue
        by_id.setdefault(case_id, []).append(trace)

    results: list[dict[str, Any]] = []
    for seed in seeds:
        case_id = seed["id"]
        records = by_id.get(case_id, [])
        if not records:
            results.append({"case_id": case_id, "status": "NOTRUN", "reason": "no captured trace"})
            continue
        if len(records) != 1:
            results.append({"case_id": case_id, "status": "NOTRUN", "reason": "duplicate traces for case_id"})
            errors.append(f"case {case_id}: duplicate traces")
            continue
        trace = records[0]
        reads = trace.get("skill_reads")
        if not isinstance(reads, list) or not all(isinstance(read, str) for read in reads):
            results.append({"case_id": case_id, "status": "NOTRUN", "reason": "skill_reads must be a list of strings"})
            errors.append(f"case {case_id}: invalid skill_reads")
            continue
        expected = seed.get("expected_reads")
        allowed = seed.get("allowed_companions", [])
        if not isinstance(expected, list) or not all(isinstance(x, str) for x in expected) or not isinstance(allowed, list) or not all(isinstance(x, str) for x in allowed):
            results.append({"case_id": case_id, "status": "NOTRUN", "reason": "invalid expected read declarations"})
            errors.append(f"case {case_id}: invalid expected_reads/allowed_companions")
            continue
        primary = seed.get("skill")
        if seed.get("should_trigger") is False and primary in allowed:
            results.append({"case_id": case_id, "status": "NOTRUN", "reason": "negative probe primary listed as allowed companion"})
            errors.append(f"case {case_id}: negative probe primary must not be an allowed companion")
            continue
        handoffs = trace.get("handoffs", [])
        stop_decision = trace.get("stop_decision")
        if not isinstance(handoffs, list) or not all(isinstance(item, str) for item in handoffs):
            results.append({"case_id": case_id, "status": "NOTRUN", "reason": "handoffs must be a list of strings"})
            errors.append(f"case {case_id}: invalid handoffs")
            continue
        if "stop_decision" in trace and type(stop_decision) is not bool:
            results.append({"case_id": case_id, "status": "NOTRUN", "reason": "stop_decision must be boolean"})
            errors.append(f"case {case_id}: invalid stop_decision")
            continue
        mismatches = []
        unrecorded = []
        actual_set = set(reads)
        expected_set = set(expected)
        unexpected = actual_set - expected_set - set(allowed)
        missing = expected_set - actual_set
        if missing:
            mismatches.append(f"missing expected reads: {sorted(missing)}")
        if unexpected:
            mismatches.append(f"unexpected reads: {sorted(unexpected)}")
        if "expected_handoffs" in seed:
            wanted_handoffs = seed["expected_handoffs"]
            if not isinstance(wanted_handoffs, list) or not all(isinstance(x, str) for x in wanted_handoffs):
                results.append({"case_id": case_id, "status": "NOTRUN", "reason": "invalid expected_handoffs declaration"})
                errors.append(f"case {case_id}: invalid expected_handoffs")
                continue
            if "handoffs" not in trace:
                unrecorded.append("expected handoffs were not recorded")
            elif handoffs != wanted_handoffs:
                mismatches.append(f"handoff mismatch: expected {wanted_handoffs}, observed {handoffs}")
        if "expected_stop_decision" in seed:
            wanted_stop = seed["expected_stop_decision"]
            if type(wanted_stop) is not bool:
                results.append({"case_id": case_id, "status": "NOTRUN", "reason": "invalid expected_stop_decision declaration"})
                errors.append(f"case {case_id}: invalid expected_stop_decision")
                continue
            if "stop_decision" not in trace:
                unrecorded.append("expected stop decision was not recorded")
            elif stop_decision is not wanted_stop:
                mismatches.append(f"stop decision mismatch: expected {wanted_stop}, observed {stop_decision}")
        status = "FAIL" if mismatches else "NOTRUN" if unrecorded else "PASS"
        results.append({"case_id": case_id, "status": status,
                        "reason": "; ".join(unrecorded) if unrecorded else None,
                        "observed_reads": reads, "observed_handoffs": handoffs if "handoffs" in trace else None,
                        "observed_stop_decision": stop_decision if "stop_decision" in trace else None,
                        "mismatches": mismatches})
    return _report(results, errors, scope)


def _report(cases: list[dict[str, Any]], errors: list[str], scope: str) -> dict[str, Any]:
    counts = {status.lower(): sum(case.get("status") == status for case in cases) for status in ("PASS", "FAIL", "NOTRUN")}
    if counts["fail"]:
        status = "FAIL"
    elif counts["notrun"] or errors:
        status = "NOTRUN"
    else:
        status = "PASS"
    return {"status": status, "scope": scope, "summary": counts, "cases": cases, "errors": errors}


def load_json(path: Path) -> tuple[Any, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"trace file not found: {path}"
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"cannot read trace JSON {path}: {exc}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=Path, default=DEFAULT_SEEDS)
    parser.add_argument("--traces", type=Path, default=DEFAULT_TRACES)
    parser.add_argument("--output", type=Path, help="write JSON report here; default prints to stdout")
    args = parser.parse_args(argv)
    seeds, seed_error = load_json(args.seeds)
    traces, trace_error = load_json(args.traces)
    if seed_error:
        report = _report([], [seed_error], "Captured skill-read traces only; no routing or generation is performed.")
        report["status"] = "NOTRUN"
    else:
        scope = "Captured skill-read traces only; this evaluator performs no routing or generation."
        report = evaluate_data(seeds, traces, trace_error=trace_error, scope=scope)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["status"] == "PASS" else 2 if report["status"] == "NOTRUN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
