#!/usr/bin/env python3
"""NTF Standard Algorithm v1.1 - pattern-based semantic folding."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

NTF_VOCAB: List[str] = [
    "Flux",
    "Anchor",
    "Drift",
    "Pulse",
    "Mirror",
    "Weave",
    "Relay",
    "Horizon",
    "Resonance",
    "Folding",
    "Consensus",
    "Overclock",
    "Deployment",
    "Checkpoint",
    "Synthesis",
    "State",
]

KEYWORD_MAP: Dict[str, str] = {
    "flux": "Flux",
    "change": "Flux",
    "anchor": "Anchor",
    "baseline": "Anchor",
    "drift": "Drift",
    "deviation": "Drift",
    "pulse": "Pulse",
    "heartbeat": "Pulse",
    "mirror": "Mirror",
    "reflect": "Mirror",
    "weave": "Weave",
    "combine": "Weave",
    "relay": "Relay",
    "handoff": "Relay",
    "horizon": "Horizon",
    "future": "Horizon",
    "resonance": "Resonance",
    "align": "Resonance",
    "fold": "Folding",
    "compress": "Folding",
    "consensus": "Consensus",
    "agree": "Consensus",
    "overclock": "Overclock",
    "accelerate": "Overclock",
    "deploy": "Deployment",
    "release": "Deployment",
    "checkpoint": "Checkpoint",
    "snapshot": "Checkpoint",
    "synthesis": "Synthesis",
    "merge": "Synthesis",
    "state": "State",
    "context": "State",
}


@dataclass
class CompressionResult:
    original_words: int
    compressed_tokens: int
    coverage: float
    ratio: float
    diversity: float
    intfr: float
    used_vocab: List[str]
    clusters: Dict[str, List[str]]


def normalize_text(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9']+", text.lower())


def detect_patterns(tokens: List[str], min_freq: int = 3) -> Counter:
    counts: Counter = Counter()
    for n in (2, 3):
        for i in range(0, len(tokens) - n + 1):
            counts[" ".join(tokens[i : i + n])] += 1
    return Counter({k: v for k, v in counts.items() if v >= min_freq})


def semantic_cluster(tokens: List[str]) -> Dict[str, List[str]]:
    clusters: Dict[str, List[str]] = defaultdict(list)
    for token in tokens:
        mapped = KEYWORD_MAP.get(token)
        if mapped:
            clusters[mapped].append(token)
    return dict(clusters)


def compress_tokens(tokens: List[str]) -> Tuple[List[str], int, List[str]]:
    compressed: List[str] = []
    replaced = 0
    used_vocab = set()
    idx = 0

    while idx < len(tokens):
        current = KEYWORD_MAP.get(tokens[idx])
        if not current:
            compressed.append(tokens[idx])
            idx += 1
            continue

        run: List[str] = []
        while idx < len(tokens):
            mapped = KEYWORD_MAP.get(tokens[idx])
            if not mapped:
                break
            run.append(mapped)
            used_vocab.add(mapped)
            idx += 1

        replaced += len(run)
        unique_run = sorted(set(run))
        if len(run) >= 2:
            compressed.append("<NTF:" + "+".join(v[:3].upper() for v in unique_run[:4]) + ">")
        else:
            compressed.append("<" + run[0][:3].upper() + ">")

    return compressed, replaced, sorted(used_vocab)


def compute_intfr(coverage: float, ratio: float, diversity: float) -> float:
    """INTFR = (coverage * ratio * diversity) * 10"""
    return round((coverage * ratio * diversity) * 10, 1)


def run_ntf(text: str) -> CompressionResult:
    tokens = normalize_text(text)
    if not tokens:
        return CompressionResult(0, 0, 0.0, 0.0, 0.0, 0.0, [], {})

    _patterns = detect_patterns(tokens)
    clusters = semantic_cluster(tokens)
    compressed, replaced, used_vocab = compress_tokens(tokens)

    original_words = len(tokens)
    compressed_tokens = len(compressed)

    coverage = replaced / original_words
    raw_ratio = original_words / compressed_tokens if compressed_tokens else 0.0
    ratio = min(raw_ratio / 10, 1.0)
    diversity = len(used_vocab) / len(NTF_VOCAB)

    return CompressionResult(
        original_words=original_words,
        compressed_tokens=compressed_tokens,
        coverage=round(coverage, 2),
        ratio=round(ratio, 2),
        diversity=round(diversity, 2),
        intfr=compute_intfr(coverage, ratio, diversity),
        used_vocab=used_vocab,
        clusters=clusters,
    )


def build_benchmark_corpus(target_words: int = 4500) -> str:
    mapped_segment = "anchor drift pulse mirror relay consensus synthesis state "
    filler_segment = "agent packet channel timeline update signal route lattice module "
    seed = normalize_text((mapped_segment * 11) + filler_segment)
    words = (seed * math.ceil(target_words / len(seed)))[:target_words]
    return " ".join(words)


def benchmark() -> CompressionResult:
    return run_ntf(build_benchmark_corpus(4500))


def main() -> None:
    parser = argparse.ArgumentParser(description="NTF Standard Algorithm v1.1")
    parser.add_argument("--text", type=str, help="Text input for compression")
    parser.add_argument("--benchmark", action="store_true", help="Run 4,500-word benchmark")
    parser.add_argument("--json", action="store_true", help="Return JSON output")
    args = parser.parse_args()

    if args.benchmark:
        result = benchmark()
    elif args.text:
        result = run_ntf(args.text)
    else:
        parser.error("Provide --text or --benchmark")

    payload = {
        "original_words": result.original_words,
        "compressed_tokens": result.compressed_tokens,
        "compression_x": round(result.original_words / result.compressed_tokens, 2)
        if result.compressed_tokens
        else 0.0,
        "coverage": result.coverage,
        "ratio": result.ratio,
        "diversity": result.diversity,
        "intfr": result.intfr,
        "used_vocab": result.used_vocab,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
