#!/usr/bin/env python3

from pathlib import Path

from ntf_multimodal_benchmark import load_jsonl, run_benchmark


def test_load_jsonl_dataset():
    rows = load_jsonl(Path("eval/datasets/multimodal_regression.jsonl"))
    assert len(rows) >= 3
    assert all("text" in r for r in rows)


def test_run_benchmark_summary_and_results():
    out = run_benchmark(Path("eval/datasets/multimodal_regression.jsonl"))
    assert out["summary"]["cases"] >= 3
    assert "avg_rdf" in out["summary"]
    assert "avg_scs" in out["summary"]
    assert "avg_ssr" in out["summary"]
    assert all("risk_level" in r for r in out["results"])
