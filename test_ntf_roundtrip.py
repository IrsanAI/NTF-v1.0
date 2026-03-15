#!/usr/bin/env python3

from ntf_multimodal_pipeline import detect_segments, compress_segments, decode_segments, run_pipeline


def test_detect_segments_mixed_markdown():
    text = """Agent context with flux and anchor.

```python
print('hello')
```

{"b": 1, "a": 2}
"""
    segments = detect_segments(text)
    kinds = [s.kind for s in segments]
    assert kinds == ["text", "code", "json"]


def test_roundtrip_preserves_code_block():
    text = """Before block.

```python
x = 1
print(x)
```

After block with consensus."""
    payload = compress_segments(detect_segments(text))
    decoded = decode_segments(payload)
    assert "```python" in decoded
    assert "x = 1" in decoded
    assert "print(x)" in decoded


def test_roundtrip_json_canonicalization():
    text = """{"z": 1, "a": 2}"""
    payload = compress_segments(detect_segments(text))
    decoded = decode_segments(payload)
    assert decoded == '{"a": 2, "z": 1}'


def test_pipeline_is_deterministic():
    text = """Flux anchor drift.

```js
console.log('x')
```
"""
    first = run_pipeline(text)
    second = run_pipeline(text)
    assert first["payload"] == second["payload"]
    assert first["decoded"] == second["decoded"]
