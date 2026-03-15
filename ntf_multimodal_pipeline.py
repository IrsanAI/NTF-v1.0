#!/usr/bin/env python3
"""NTF Multimodal Pipeline v0.1

Goal:
- detect mixed segments (text/code/json)
- compress text segments with NTF
- preserve structural segments for deterministic decode
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Literal

from ntf_standard import run_ntf

SegmentType = Literal["text", "code", "json"]


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


def _looks_like_json(block: str) -> bool:
    stripped = block.strip()
    if not stripped:
        return False
    if not ((stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]"))):
        return False
    try:
        json.loads(stripped)
        return True
    except Exception:
        return False


def detect_segments(input_text: str) -> List[Segment]:
    """Detect text/code/json segments, preserving order."""
    segments: List[Segment] = []
    cursor = 0

    for match in re.finditer(r"```([a-zA-Z0-9_+-]*)\n(.*?)```", input_text, flags=re.DOTALL):
        pre = input_text[cursor:match.start()]
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
                        "compression_x": round((result.original_words / result.compressed_tokens), 2) if result.compressed_tokens else 0.0,
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

    payload = PipelinePayload(schema="ntf.multimodal", version="0.1", segments=compressed)
    return {
        "schema": payload.schema,
        "version": payload.version,
        "segments": [asdict(s) for s in payload.segments],
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
    payload = compress_segments(segments)
    decoded = decode_segments(payload)
    return {
        "segments_detected": len(segments),
        "payload": payload,
        "decoded": decoded,
    }
