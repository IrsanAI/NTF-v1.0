#!/usr/bin/env python3

import json
from pathlib import Path

from ntf_multimodal_benchmark import (
    append_history_entry,
    check_thresholds,
    load_jsonl,
    persist_results,
    run_benchmark,
)


def test_load_jsonl_dataset():
    rows = load_jsonl(Path("eval/datasets/multimodal_regression.jsonl"))
    assert len(rows) >= 3
    assert all("text" in r for r in rows)


def test_expanded_datasets_scale_targets():
    rows_120 = load_jsonl(Path("eval/datasets/multimodal_expanded_120.jsonl"))
    rows_600 = load_jsonl(Path("eval/datasets/multimodal_expanded_600.jsonl"))
    assert len(rows_120) >= 100
    assert len(rows_600) >= 500


def test_run_benchmark_summary_and_results():
    out = run_benchmark(Path("eval/datasets/multimodal_regression.jsonl"))
    summary = out["summary"]
    assert summary["cases"] >= 3
    assert "avg_rdf" in summary and "avg_scs" in summary and "avg_ssr" in summary
    assert "min_case_rdf" in summary and "min_case_scs" in summary and "min_case_ssr" in summary
    assert "generated_at" in summary
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
    flags = check_thresholds(
        out,
        min_rdf=90,
        min_scs=90,
        min_ssr=40,
        min_case_rdf=90,
        min_case_scs=90,
        min_case_ssr=30,
    )
    assert flags["pass_rdf"] is True
    assert flags["pass_scs"] is True
    assert flags["pass_ssr"] is True
    assert flags["pass_case_rdf"] is True
    assert flags["pass_case_scs"] is True
    assert flags["pass_case_ssr"] is True


def test_append_history_entry_has_delta(tmp_path):
    out = run_benchmark(Path("eval/datasets/multimodal_regression.jsonl"))
    hist_path = tmp_path / "hist.json"
    first = append_history_entry(out, hist_path)
    second = append_history_entry(out, hist_path)
    assert hist_path.exists()
    assert len(first["runs"]) == 1
    assert len(second["runs"]) == 2
    assert "delta_avg_rdf" in second["runs"][-1]
    assert "delta_avg_scs" in second["runs"][-1]
    assert "delta_avg_ssr" in second["runs"][-1]
