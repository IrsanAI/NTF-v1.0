# Multimodal Benchmark Results

Dieses Verzeichnis enthält versionierbare Benchmark-Reports der NTF-Multimodal-Pipeline.

Beispiel:

```bash
python3 ntf_multimodal_benchmark.py \
  --dataset eval/datasets/multimodal_regression.jsonl \
  --output eval/results/multimodal_latest.json \
  --json
```

Die CI-Pipeline erzeugt ebenfalls `multimodal_latest.json` als Artifact.
