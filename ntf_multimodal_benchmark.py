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
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": str(path),
    }

    return {"summary": summary, "results": results}


def persist_results(report: Dict[str, object], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run multimodal benchmark")
    parser.add_argument(
        "--dataset",
        default="eval/datasets/multimodal_regression.jsonl",
        help="Path to JSONL dataset",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument(
        "--output",
        default="",
        help="Optional output JSON file path (e.g. eval/results/multimodal_latest.json)",
    )
    args = parser.parse_args()

    data = run_benchmark(Path(args.dataset))

    if args.output:
        persist_results(data, Path(args.output))

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("cases:", data["summary"]["cases"])
        print("avg_rdf:", data["summary"]["avg_rdf"])
        print("avg_scs:", data["summary"]["avg_scs"])
        print("avg_ssr:", data["summary"]["avg_ssr"])
        if args.output:
            print("output:", args.output)


if __name__ == "__main__":
    main()
