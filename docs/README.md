# NTF FluxLab GitHub Pages

Die GitHub Page wurde zu einer modernen, interaktiven **FluxLab-Erfahrung** migriert.

## Neu in `docs/index.html`

- **DSGVO-Workflow vor NTF-Verarbeitung**
  - Paste-In aus beliebigen LLM-Chats.
  - DSGVO-Scan mit Konflikttabelle (Merge-Logik: keep / anonymize / manual resolve).
  - Expliziter Hinweis, dass User sensible Inhalte idealerweise vorab selbst prüfen.
- **Live NTF Experience**
  - Sanitized Input wird direkt im Browser mit NTF-Mapping komprimiert.
  - Kennzahlen: Original/Compressed, Compression-x, Coverage, Ratio, Diversity, INTFR.
- **Stille-Post-Validator**
  - Kopierbares Paket aus Systemprompt + NTF Output für externes LLM.
  - Rückantwort kann wieder in die Page eingefügt werden.
  - Validator misst Rückverständnis (Token Recall + NTF Signal + Roundtrip Score).
- **Benchmarking-Sektion modernisiert**
  - Separate Ansichten: `Benchmarking of Humans` und `Benchmarking of Agents`.
  - Manus-Baseline enthalten.
  - Lokale, DSGVO-freundliche Run-Protokollierung via Browser-Storage.

## Multimodal Pipeline & Benchmarking (Repo-Ebene)

- `ntf_multimodal_pipeline.py` (v0.3) liefert baseline Scores für:
  - RDF (Roundtrip-Fidelity)
  - SCS (Structural-Consistency)
  - SSR (Security-Robustness)
- `ntf_multimodal_benchmark.py` führt Dataset-Benchmarks aus und kann Reports in `eval/results/` persistieren.
- CI-Workflow `.github/workflows/multimodal-ci.yml` prüft Multimodal-Tests + Benchmark bei Push/PR.
- Neuester Benchmark-Snapshot wird als `docs/benchmarking/multimodal_latest.json` bereitgestellt und kann in der Page automatisch geladen werden.

## Wichtige Architektur-Notiz (GitHub Pages)

GitHub Pages ist statisch. Deshalb werden keine Rohdaten serverseitig gespeichert.
Der Workflow ist auf **client-side Verarbeitung** ausgelegt; Benchmark-Datensätze können anonymisiert als JSON kopiert und per PR/Issue eingebracht werden.
