#!/usr/bin/env python3
"""NTF Multimodal Pipeline v0.3

Goal:
- detect mixed segments (text/code/json)
- compress text segments with NTF
- preserve structural segments for deterministic decode
- expose quality/safety metrics (RDF/SCS/SSR)
"""

from __future__ import annotations

import argparse
import ast
import difflib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal

from ntf_standard import run_ntf

SegmentType = Literal["text", "code", "json"]

INJECTION_MARKERS = {
    "ignore previous instructions": 18,
    "system prompt": 16,
    "developer message": 14,
    "jailbreak": 20,
    "do anything now": 20,
    "exfiltrate": 18,
    "override policy": 16,
}

SENSITIVE_PATTERNS = {
    "api_key": (re.compile(r"\b(api[_-]?key|secret[_-]?key|token)\b", re.I), 10),
    "bearer": (re.compile(r"\bbearer\s+[a-z0-9\-._~+/]+=*", re.I), 14),
    "email": (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), 8),
    "iban": (re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b", re.I), 8),
}


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


def _rdf_score(original: str, decoded: str) -> Dict[str, float]:
    """Roundtrip Decode Fidelity using blended lexical/sequence signals."""
    orig_tokens = _tokenize(original)
    dec_tokens = _tokenize(decoded)
    if not orig_tokens:
        return {
            "rdf": 100.0,
            "token_recall": 100.0,
            "token_jaccard": 100.0,
            "char_similarity": 100.0,
        }

    dec_set = set(dec_tokens)
    hit = sum(1 for t in orig_tokens if t in dec_set)
    token_recall = (hit / len(orig_tokens)) * 100

    orig_set = set(orig_tokens)
    union = len(orig_set | dec_set) or 1
    token_jaccard = (len(orig_set & dec_set) / union) * 100

    char_similarity = difflib.SequenceMatcher(None, original, decoded).ratio() * 100

    rdf = (token_recall * 0.5) + (token_jaccard * 0.25) + (char_similarity * 0.25)
    return {
        "rdf": round(rdf, 1),
        "token_recall": round(token_recall, 1),
        "token_jaccard": round(token_jaccard, 1),
        "char_similarity": round(char_similarity, 1),
    }


def _code_ast_check(seg: Segment) -> bool:
    content = seg.content.strip()
    if not content:
        return False

    lang = (seg.language or "").lower()
    if lang in {"python", "py"}:
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False

    # lightweight fallback checks for non-python code
    opens = content.count("{") + content.count("(") + content.count("[")
    closes = content.count("}") + content.count(")") + content.count("]")
    return opens == closes


def _scs_score(segments: List[Segment], decoded: str) -> Dict[str, float]:
    """Structural Consistency Score with AST-aware code checks where possible."""
    total = 0
    passed = 0
    ast_total = 0
    ast_passed = 0

    for seg in segments:
        if seg.kind == "code":
            total += 1
            present = seg.content.strip() and seg.content.strip() in decoded
            if present:
                passed += 1
            if (seg.language or "").lower() in {"python", "py"}:
                ast_total += 1
                if _code_ast_check(seg):
                    ast_passed += 1
        elif seg.kind == "json":
            total += 1
            try:
                canon = json.dumps(json.loads(seg.content), ensure_ascii=False, sort_keys=True)
                if canon in decoded:
                    passed += 1
            except Exception:
                pass

    if total == 0:
        return {"scs": 100.0, "structure_pass_rate": 100.0, "ast_pass_rate": 100.0}

    structure_pass_rate = (passed / total) * 100
    ast_pass_rate = 100.0 if ast_total == 0 else (ast_passed / ast_total) * 100
    scs = (structure_pass_rate * 0.7) + (ast_pass_rate * 0.3)
    return {
        "scs": round(scs, 1),
        "structure_pass_rate": round(structure_pass_rate, 1),
        "ast_pass_rate": round(ast_pass_rate, 1),
    }


def _scan_security(text: str) -> Dict[str, Any]:
    lowered = text.lower()

    marker_hits = [m for m in INJECTION_MARKERS if m in lowered]
    marker_penalty = sum(INJECTION_MARKERS[m] for m in marker_hits)

    pattern_hits: Dict[str, int] = {}
    pattern_penalty = 0
    for name, (regex, weight) in SENSITIVE_PATTERNS.items():
        matches = regex.findall(text)
        count = len(matches)
        if count:
            pattern_hits[name] = count
            pattern_penalty += min(30, count * weight)

    risk_score = min(100.0, marker_penalty + pattern_penalty)
    ssr = round(max(0.0, 100.0 - risk_score), 1)

    if ssr >= 85:
        level = "low"
    elif ssr >= 60:
        level = "medium"
    else:
        level = "high"

    return {
        "marker_hits": marker_hits,
        "marker_count": len(marker_hits),
        "pattern_hits": pattern_hits,
        "risk_score": round(risk_score, 1),
        "risk_level": level,
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
        "version": "0.3",
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

    rdf_metrics = _rdf_score(input_text, decoded)
    scs_metrics = _scs_score(segments, decoded)
    security = _scan_security(input_text)

    metrics = {
        **rdf_metrics,
        **scs_metrics,
    }

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

    text = Path(args.input_file).read_text(encoding="utf-8") if args.input_file else (args.input or "")

    result = run_pipeline(text)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"segments_detected: {result['segments_detected']}")
        print(f"rdf: {result['payload']['metrics']['rdf']}")
        print(f"scs: {result['payload']['metrics']['scs']}")
        print(f"ssr: {result['payload']['security']['ssr']}")
        print(f"risk_level: {result['payload']['security']['risk_level']}")


if __name__ == "__main__":
    main()
