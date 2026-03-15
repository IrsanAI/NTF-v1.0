#!/usr/bin/env python3

import json
from pathlib import Path

from ntf_multimodal_benchmark import check_thresholds, load_jsonl, persist_results, run_benchmark


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
    assert "generated_at" in out["summary"]
    assert all("risk_level" in r for r in out["results"])


def test_persist_results(tmp_path):
    out = run_benchmark(Path("eval/datasets/multimodal_regression.jsonl"))
    target = tmp_path / "results" / "multi.json"
    persist_results(out, target)
    assert target.exists()
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded["summary"]["cases"] == out["summary"]["cases"]


def test_threshold_checks_return_flags():
    out = run_benchmark(Path("eval/datasets/multimodal_regression.jsonl"))
    flags = check_thresholds(out, min_rdf=90, min_scs=90, min_ssr=40)
    assert flags["pass_rdf"] is True
    assert flags["pass_scs"] is True
    assert flags["pass_ssr"] is True
