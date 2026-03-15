#!/usr/bin/env python3
"""Benchmark runner for NTF multimodal pipeline."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Dict, List

from ntf_multimodal_pipeline import run_pipeline


def load_jsonl(path: Path) -> List[Dict[str, str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def run_benchmark(path: Path) -> Dict[str, object]:
    rows = load_jsonl(path)
    results = []

    for row in rows:
        out = run_pipeline(row["text"])
        metrics = out["payload"]["metrics"]
        security = out["payload"]["security"]
        results.append(
            {
                "id": row.get("id", "unknown"),
                "segments_detected": out["segments_detected"],
                "rdf": metrics["rdf"],
                "scs": metrics["scs"],
                "ssr": security["ssr"],
                "risk_level": security["risk_level"],
            }
        )

    summary = {
        "cases": len(results),
        "avg_rdf": round(mean([r["rdf"] for r in results]), 2) if results else 0.0,
        "avg_scs": round(mean([r["scs"] for r in results]), 2) if results else 0.0,
        "avg_ssr": round(mean([r["ssr"] for r in results]), 2) if results else 0.0,
        "min_case_rdf": round(min((r["rdf"] for r in results), default=0.0), 2),
        "min_case_scs": round(min((r["scs"] for r in results), default=0.0), 2),
        "min_case_ssr": round(min((r["ssr"] for r in results), default=0.0), 2),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": str(path),
    }

    return {"summary": summary, "results": results}


def persist_results(report: Dict[str, object], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def append_history_entry(report: Dict[str, object], history_path: Path) -> Dict[str, object]:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    if history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))
    else:
        history = {"runs": []}

    summary = report.get("summary", {})
    entry = {
        "generated_at": summary.get("generated_at"),
        "dataset": summary.get("dataset"),
        "cases": summary.get("cases"),
        "avg_rdf": summary.get("avg_rdf"),
        "avg_scs": summary.get("avg_scs"),
        "avg_ssr": summary.get("avg_ssr"),
        "min_case_rdf": summary.get("min_case_rdf"),
        "min_case_scs": summary.get("min_case_scs"),
        "min_case_ssr": summary.get("min_case_ssr"),
    }

    runs = history.setdefault("runs", [])
    prev = runs[-1] if runs else None
    if prev:
        entry["delta_avg_rdf"] = round(float(entry["avg_rdf"]) - float(prev.get("avg_rdf", 0.0)), 2)
        entry["delta_avg_scs"] = round(float(entry["avg_scs"]) - float(prev.get("avg_scs", 0.0)), 2)
        entry["delta_avg_ssr"] = round(float(entry["avg_ssr"]) - float(prev.get("avg_ssr", 0.0)), 2)
    else:
        entry["delta_avg_rdf"] = 0.0
        entry["delta_avg_scs"] = 0.0
        entry["delta_avg_ssr"] = 0.0

    runs.append(entry)
    history["runs"] = runs[-100:]
    history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    return history


def check_thresholds(
    report: Dict[str, object],
    min_rdf: float,
    min_scs: float,
    min_ssr: float,
    min_case_rdf: float,
    min_case_scs: float,
    min_case_ssr: float,
) -> Dict[str, object]:
    summary = report["summary"]
    return {
        "pass_rdf": float(summary["avg_rdf"]) >= min_rdf,
        "pass_scs": float(summary["avg_scs"]) >= min_scs,
        "pass_ssr": float(summary["avg_ssr"]) >= min_ssr,
        "pass_case_rdf": float(summary["min_case_rdf"]) >= min_case_rdf,
        "pass_case_scs": float(summary["min_case_scs"]) >= min_case_scs,
        "pass_case_ssr": float(summary["min_case_ssr"]) >= min_case_ssr,
        "min_rdf": min_rdf,
        "min_scs": min_scs,
        "min_ssr": min_ssr,
        "min_case_rdf": min_case_rdf,
        "min_case_scs": min_case_scs,
        "min_case_ssr": min_case_ssr,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run multimodal benchmark")
    parser.add_argument("--dataset", default="eval/datasets/multimodal_regression.jsonl", help="Path to JSONL dataset")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--output", default="", help="Optional output JSON file path")
    parser.add_argument("--docs-output", default="", help="Optional docs output path")
    parser.add_argument("--history-file", default="", help="Optional history JSON path")
    parser.add_argument("--min-rdf", type=float, default=0.0, help="Minimum avg RDF threshold")
    parser.add_argument("--min-scs", type=float, default=0.0, help="Minimum avg SCS threshold")
    parser.add_argument("--min-ssr", type=float, default=0.0, help="Minimum avg SSR threshold")
    parser.add_argument("--min-case-rdf", type=float, default=0.0, help="Minimum per-case RDF threshold")
    parser.add_argument("--min-case-scs", type=float, default=0.0, help="Minimum per-case SCS threshold")
    parser.add_argument("--min-case-ssr", type=float, default=0.0, help="Minimum per-case SSR threshold")
    parser.add_argument("--enforce-thresholds", action="store_true", help="Exit non-zero if thresholds fail")
    args = parser.parse_args()

    data = run_benchmark(Path(args.dataset))

    if args.output:
        persist_results(data, Path(args.output))
    if args.docs_output:
        persist_results(data, Path(args.docs_output))

    history_payload = None
    if args.history_file:
        history_payload = append_history_entry(data, Path(args.history_file))

    threshold_status = check_thresholds(
        data,
        args.min_rdf,
        args.min_scs,
        args.min_ssr,
        args.min_case_rdf,
        args.min_case_scs,
        args.min_case_ssr,
    )

    if args.json:
        payload = {**data, "thresholds": threshold_status}
        if history_payload is not None:
            payload["history"] = history_payload
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("cases:", data["summary"]["cases"])
        print("avg_rdf:", data["summary"]["avg_rdf"])
        print("avg_scs:", data["summary"]["avg_scs"])
        print("avg_ssr:", data["summary"]["avg_ssr"])
        print("min_case_rdf:", data["summary"]["min_case_rdf"])
        print("min_case_scs:", data["summary"]["min_case_scs"])
        print("min_case_ssr:", data["summary"]["min_case_ssr"])
        if args.output:
            print("output:", args.output)
        if args.docs_output:
            print("docs_output:", args.docs_output)
        if args.history_file:
            print("history_file:", args.history_file)
        print("thresholds:", threshold_status)

    if args.enforce_thresholds and not all(
        [
            threshold_status["pass_rdf"],
            threshold_status["pass_scs"],
            threshold_status["pass_ssr"],
            threshold_status["pass_case_rdf"],
            threshold_status["pass_case_scs"],
            threshold_status["pass_case_ssr"],
        ]
    ):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
