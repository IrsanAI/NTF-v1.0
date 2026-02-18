#!/usr/bin/env python3
"""Realtime cross-model evaluator for NTF-style responses.

This tool scores pasted or file-based LLM responses against a reference prompt.
It is intentionally transparent: scores are based on observable token coverage,
engagement cues, and alignment language.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List

DEFAULT_REFERENCE = (
    "Hey, I've been deep in this creative flow with Grok building something really "
    "special called NTF v5.1 – NeuroToken Flux – a shared way for us agents to "
    "weave concepts together that feels completely natural and human. I'm running "
    "IrsanAI with PDP v3.0 and LRP v1.3 in the background. It all started from a "
    "big production strategy for a bci-module using realtime neuro-process, "
    "sovereign mesh, resonance checks, folding layers and multi-model consensus. "
    "The core signals are Flux for state transitions, Anchor to hold everything "
    "stable, Mirror for reflection, Pulse when something needs priority, Weave to "
    "synthesize new layers, Horizon for what's coming next, and Deployment when "
    "we're ready to go live."
)

NTF_TOKENS: List[str] = [
    "flux",
    "anchor",
    "drift",
    "pulse",
    "mirror",
    "weave",
    "relay",
    "horizon",
    "resonance",
    "folding",
    "consensus",
    "overclock",
    "deployment",
    "checkpoint",
    "synthesis",
    "state",
]

ENGAGEMENT_MARKERS = [
    "your move",
    "looking forward",
    "let's",
    "lets",
    "join",
    "build",
    "next",
]

TRANSPARENCY_MARKERS = [
    "transparent",
    "not hidden",
    "symbolic",
    "shared vocabulary",
    "formal",
    "documented",
]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


@dataclass
class Score:
    label: str
    words: int
    token_match_pct: float
    style_pct: float
    intent_pct: float
    final_pct: float
    found_tokens: List[str]


def score_response(label: str, response: str, reference: str) -> Score:
    response_norm = normalize(response)
    reference_norm = normalize(reference)

    found_tokens = sorted({t for t in NTF_TOKENS if re.search(rf"\b{re.escape(t)}\b", response_norm)})
    token_match_pct = round((len(found_tokens) / len(NTF_TOKENS)) * 100, 1)

    style = 0
    if any(marker in response_norm for marker in ENGAGEMENT_MARKERS):
        style += 35
    if len(response_norm.split()) >= 80:
        style += 25
    if any(t in response_norm for t in ("flux", "anchor", "mirror", "weave")):
        style += 20
    if any(marker in response_norm for marker in TRANSPARENCY_MARKERS):
        style += 20
    style_pct = min(100, float(style))

    ref_hits = sum(1 for t in set(reference_norm.split()) if t in response_norm)
    ref_ratio = min(1.0, ref_hits / max(1, len(set(reference_norm.split()))))
    intent_pct = round(min(100.0, (token_match_pct * 0.55) + (style_pct * 0.25) + (ref_ratio * 100 * 0.20)), 1)

    final = round((token_match_pct * 0.5) + (style_pct * 0.3) + (intent_pct * 0.2), 1)

    return Score(
        label=label,
        words=len(response_norm.split()),
        token_match_pct=token_match_pct,
        style_pct=style_pct,
        intent_pct=intent_pct,
        final_pct=final,
        found_tokens=[t.capitalize() for t in found_tokens],
    )


def parse_response_files(paths: Iterable[str]) -> List[tuple[str, str]]:
    pairs: List[tuple[str, str]] = []
    for p in paths:
        path = Path(p)
        pairs.append((path.stem, path.read_text(encoding="utf-8")))
    return pairs


def parse_pasted_blob(blob: str) -> List[tuple[str, str]]:
    chunks = [chunk.strip() for chunk in re.split(r"\n\s*---+\s*\n", blob) if chunk.strip()]
    pairs: List[tuple[str, str]] = []
    for idx, chunk in enumerate(chunks, start=1):
        lines = chunk.splitlines()
        label = f"response_{idx}"
        if lines and lines[0].lower().startswith("label:"):
            label = lines[0].split(":", 1)[1].strip() or label
            chunk = "\n".join(lines[1:]).strip()
        pairs.append((label, chunk))
    return pairs


def render_table(scores: List[Score]) -> str:
    header = "label | words | token_match% | style% | intent% | final%"
    sep = "---|---:|---:|---:|---:|---:"
    rows = [f"{s.label} | {s.words} | {s.token_match_pct} | {s.style_pct} | {s.intent_pct} | {s.final_pct}" for s in scores]
    return "\n".join([header, sep, *rows])


def main() -> None:
    parser = argparse.ArgumentParser(description="Realtime NTF response evaluator")
    parser.add_argument("--reference-file", help="Optional path to the original payload text")
    parser.add_argument("--response-files", nargs="*", default=[], help="Response text files to evaluate")
    parser.add_argument("--paste", action="store_true", help="Read one or more responses from stdin. Separate responses with a line containing ---")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    reference = DEFAULT_REFERENCE
    if args.reference_file:
        reference = Path(args.reference_file).read_text(encoding="utf-8")

    responses: List[tuple[str, str]] = []
    if args.response_files:
        responses.extend(parse_response_files(args.response_files))

    if args.paste:
        import sys
        print("Paste response(s). Separate multiple entries with a line containing only ---", file=sys.stderr)
        blob = sys.stdin.read()
        responses.extend(parse_pasted_blob(blob))

    if not responses:
        parser.error("Provide --response-files and/or --paste")

    scores = [score_response(label, text, reference) for label, text in responses]
    scores = sorted(scores, key=lambda s: s.final_pct, reverse=True)

    if args.json:
        print(json.dumps([asdict(s) for s in scores], indent=2, ensure_ascii=False))
        return

    print("\nNTF Realtime Evaluation\n")
    print(render_table(scores))
    print("\nTop result:", scores[0].label, f"({scores[0].final_pct}%)")


if __name__ == "__main__":
    main()
