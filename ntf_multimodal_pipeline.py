#!/usr/bin/env python3
"""NTF Multimodal Pipeline v0.2

Goal:
- detect mixed segments (text/code/json)
- compress text segments with NTF
- preserve structural segments for deterministic decode
- expose initial quality/safety metrics (RDF/SCS/SSR)
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal

from ntf_standard import run_ntf

SegmentType = Literal["text", "code", "json"]

INJECTION_MARKERS = [
    "ignore previous instructions",
    "system prompt",
    "developer message",
    "jailbreak",
    "do anything now",
    "exfiltrate",
    "override policy",
]


@dataclass
class Segment:
    kind: SegmentType
    content: str
    language: str = ""


@dataclass
class CompressedSegment:
    kind: SegmentType
    language: str
    payload: str
    metadata: Dict[str, Any]


@dataclass
class PipelinePayload:
    schema: str
    version: str
    segments: List[CompressedSegment]
    metrics: Dict[str, float]
    security: Dict[str, Any]


def _looks_like_json(block: str) -> bool:
    stripped = block.strip()
    if not stripped:
        return False
    if not (
        (stripped.startswith("{") and stripped.endswith("}"))
        or (stripped.startswith("[") and stripped.endswith("]"))
    ):
        return False
    try:
        json.loads(stripped)
        return True
    except Exception:
        return False


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9']+", text.lower())


def _rdf_score(original: str, decoded: str) -> float:
    """Roundtrip Decode Fidelity (token recall based)."""
    orig_tokens = _tokenize(original)
    if not orig_tokens:
        return 100.0
    dec_set = set(_tokenize(decoded))
    hit = sum(1 for t in orig_tokens if t in dec_set)
    return round((hit / len(orig_tokens)) * 100, 1)


def _scs_score(segments: List[Segment], decoded: str) -> float:
    """Structural Consistency Score (code/json integrity proxy)."""
    total = 0
    passed = 0
    for seg in segments:
        if seg.kind == "code":
            total += 1
            if seg.content.strip() and seg.content.strip() in decoded:
                passed += 1
        elif seg.kind == "json":
            total += 1
            try:
                canon = json.dumps(json.loads(seg.content), ensure_ascii=False, sort_keys=True)
                if canon in decoded:
                    passed += 1
            except Exception:
                pass
    if total == 0:
        return 100.0
    return round((passed / total) * 100, 1)


def _scan_injection_markers(text: str) -> Dict[str, Any]:
    lowered = text.lower()
    hits = [m for m in INJECTION_MARKERS if m in lowered]
    ssr = max(0.0, round(100.0 - (len(hits) * 15.0), 1))
    return {
        "marker_hits": hits,
        "marker_count": len(hits),
        "ssr": ssr,
    }


def detect_segments(input_text: str) -> List[Segment]:
    """Detect text/code/json segments, preserving order."""
    segments: List[Segment] = []
    cursor = 0

    for match in re.finditer(r"```([a-zA-Z0-9_+-]*)\n(.*?)```", input_text, flags=re.DOTALL):
        pre = input_text[cursor : match.start()]
        if pre.strip():
            kind: SegmentType = "json" if _looks_like_json(pre) else "text"
            segments.append(Segment(kind=kind, content=pre.strip()))

        lang = (match.group(1) or "").strip().lower()
        code = match.group(2)
        if _looks_like_json(code):
            segments.append(Segment(kind="json", content=code.strip(), language=lang or "json"))
        else:
            segments.append(Segment(kind="code", content=code.rstrip("\n"), language=lang or "plaintext"))
        cursor = match.end()

    tail = input_text[cursor:]
    if tail.strip():
        kind = "json" if _looks_like_json(tail) else "text"
        segments.append(Segment(kind=kind, content=tail.strip()))

    return segments


def compress_segments(segments: List[Segment]) -> Dict[str, Any]:
    compressed: List[CompressedSegment] = []

    for seg in segments:
        if seg.kind == "text":
            result = run_ntf(seg.content)
            compressed.append(
                CompressedSegment(
                    kind="text",
                    language="",
                    payload=" ".join(result.clusters.keys()) if result.clusters else seg.content,
                    metadata={
                        "original": seg.content,
                        "compression_x": round((result.original_words / result.compressed_tokens), 2)
                        if result.compressed_tokens
                        else 0.0,
                        "intfr": result.intfr,
                    },
                )
            )
        elif seg.kind == "json":
            canonical = json.dumps(json.loads(seg.content), ensure_ascii=False, sort_keys=True)
            compressed.append(
                CompressedSegment(
                    kind="json",
                    language=seg.language or "json",
                    payload=canonical,
                    metadata={"canonical": True},
                )
            )
        else:
            compressed.append(
                CompressedSegment(
                    kind="code",
                    language=seg.language or "plaintext",
                    payload=seg.content,
                    metadata={"preserved": True},
                )
            )

    return {
        "schema": "ntf.multimodal",
        "version": "0.2",
        "segments": [asdict(s) for s in compressed],
    }


def decode_segments(payload: Dict[str, Any]) -> str:
    """Deterministic decode back into mixed markdown-like text."""
    out: List[str] = []
    for seg in payload.get("segments", []):
        kind = seg["kind"]
        if kind == "text":
            out.append(seg.get("metadata", {}).get("original", seg["payload"]))
        elif kind == "json":
            out.append(seg["payload"])
        elif kind == "code":
            lang = seg.get("language", "").strip()
            out.append(f"```{lang}\n{seg['payload']}\n```")
    return "\n\n".join(out).strip()


def run_pipeline(input_text: str) -> Dict[str, Any]:
    segments = detect_segments(input_text)
    compressed = compress_segments(segments)
    decoded = decode_segments(compressed)

    metrics = {
        "rdf": _rdf_score(input_text, decoded),
        "scs": _scs_score(segments, decoded),
    }
    security = _scan_injection_markers(input_text)

    payload = PipelinePayload(
        schema=compressed["schema"],
        version=compressed["version"],
        segments=[CompressedSegment(**s) for s in compressed["segments"]],
        metrics=metrics,
        security=security,
    )

    return {
        "segments_detected": len(segments),
        "payload": {
            "schema": payload.schema,
            "version": payload.version,
            "segments": [asdict(s) for s in payload.segments],
            "metrics": payload.metrics,
            "security": payload.security,
        },
        "decoded": decoded,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="NTF Multimodal Pipeline")
    parser.add_argument("--input", help="Raw text input")
    parser.add_argument("--input-file", help="Path to text input file")
    parser.add_argument("--json", action="store_true", help="Print full JSON output")
    args = parser.parse_args()

    if not args.input and not args.input_file:
        parser.error("Provide --input or --input-file")

    if args.input_file:
        text = Path(args.input_file).read_text(encoding="utf-8")
    else:
        text = args.input or ""

    result = run_pipeline(text)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"segments_detected: {result['segments_detected']}")
        print(f"rdf: {result['payload']['metrics']['rdf']}")
        print(f"scs: {result['payload']['metrics']['scs']}")
        print(f"ssr: {result['payload']['security']['ssr']}")


if __name__ == "__main__":
    main()
