# NTF-v1.0 Repository Analyse + Roadmap (Stand: 2026-03, aktualisiert)

## 0) Positionierung

NTF ist aktuell ein **früher Prototyp mit starker Messbarkeit und klarer Skalierungshypothese**.
Ziel bleibt: von keyword-basierter Kompression zu robustem, struktur- und kontextbewusstem A2A-Kompressionsstandard.

---

## 1) Kurzfazit zum Intent des Repos

Das Repo verfolgt zwei verbundene Ziele:

1. **NTF als semantische Kompressionslogik messbar machen** (Algorithmus + INTFR + Benchmarking + Cross-Model-Evaluation).
2. **MindMaster als Infrastrukturpfad vorbereiten** (lokale, sichere, DSGVO-orientierte Agent-/Wissensplattform mit Connector, Vault, Governance und später A2A-Layer).

Strategischer Intent: **von einer prototypischen Kompressionsmethode zu einer belastbaren Agenten-Kommunikations- und Wissensinfrastruktur**.

---

## 2) Status-Update (konkret)

### Done
- NTF v1.1 Kern ist funktionsfähig (`ntf_standard.py`).
- Reproduzierbarer Benchmark ist vorhanden (`python3 ntf_standard.py --benchmark`).
- Cross-Model Eval und Traffic-Simulation liegen vor (`ntf_realtime_eval.py`, `ntf_agent_traffic_sim.py`).
- Moderne FluxLab GitHub Page ist umgesetzt (`docs/index.html`).
- Lizenz ergänzt (`LICENSE`).
- Test-Baseline auf 100% in der vorhandenen Suite korrigiert (INTFR-Rundungserwartung in `test_ntf_comprehensive.py`).
- **Neu:** Multimodal Pipeline v0.1 als nächster Umsetzungsschritt (`ntf_multimodal_pipeline.py`, `test_ntf_roundtrip.py`).

### Open
- RDF/SCS/SSR Metriken noch nicht als stabile API implementiert.
- Keine produktive Persistenz für Multimodal-Run-Historie.
- MindMaster-Komponenten weiterhin Skeleton-Stufe.

---

## 3) Was noch aussteht (Status: open)

### A) NTF-seitig
- Aktueller NTF-Kern ist in v1 keyword- und run-basiert.
- Für v2 fehlen noch ausgereifte Strukturmetriken (RDF, SCS) und Security-Signale (SSR).
- Safety-/Robustness-Layer gegen Prompt-Injection ist noch baseline-only.

### B) Evaluation-seitig
- Mehr reale Domänenkorpora mit Mischinhalten (Text+Code+Artefakte) nötig.
- Fehlende standardisierte Long-Context-Regression-Suite (>100k Tokens in Segmenten).

### C) MindMaster-Produktpfad
- Connectoren sind nicht produktiv an Provider-Exports angebunden.
- Data-Vault-Krypto ohne echte KMS/HSM/OQS-Integration.
- UI-/Agentic-Layer und Governance sind nur teilweise implementiert.

---

## 4) Roadmap-Vorschlag (execution-first)

## Phase R1 (0–4 Wochen): NTF v2 Foundations
**Ziel:** Von Keyword-Kompression zu struktur- und kontextbewusster Semantikkompression.

- Content-Type Detection Pipeline (text/markdown/code/json/artifact refs).
- Segmentierung vor Kompression.
- NTF-Containerformat v2 (schema/version/segment metadata/integrity fields).
- Metrikfamilie: INTFR + RDF + SCS + SSR.

## Phase R2 (4–10 Wochen): Intelligent Next-Level Detection (Pflicht-Subaufgabe)
**Ziel:** Dynamische Mischinhalte aus Text, Codeblöcken, Artefakten robust verarbeiten.

- Hierarchical Detector:
  1. coarse classifier (text/code/config/binary reference)
  2. fine parser (markdown/code AST/chunk graph)
  3. uncertainty scoring + fallback policy
- Dual-Channel Compression:
  - Channel A: semantische Verdichtung (textual context)
  - Channel B: strukturerhaltende Kompression (code/artifacts)
- Reconstruction Contracts:
  - canonical serialization
  - deterministic decoding
  - integrity checks (hash chain + segment checksums)
- Zielwerte:
  - >=98% erfolgreiche Verarbeitung heterogener Inputs
  - >=99% Roundtrip-Decode für strukturkritische Inhalte

## Phase R3 (10–16 Wochen): Large-Context Scaling
- Adaptive windowing + hierarchical memory tiers.
- Query-aware rehydration statt Full Decode.
- Cost/latency-aware routing.
- Reale Long-Context Benchmarks + Multi-Agent-Hops.

## Phase R4 (parallel ab Woche 6): MindMaster Integration
- Connector-Orchestrator produktivisieren.
- Data-Vault hardening (key lifecycle, auditability).
- Governance enforcement.
- Dashboard mit NTF-Metriken (INTFR/RDF/Drift/Freshness).

---

## 5) Aktueller nächster Schritt (fortgeführt)

Bereits umgesetzt als v0.3-Basis:
- `ntf_multimodal_pipeline.py`
  - `detect_segments(input_text)`
  - `compress_segments(segments)`
  - `decode_segments(payload)`
- `test_ntf_roundtrip.py` mit Golden-Cases:
  - gemischter Markdown+Code+JSON Input
  - Codeblock-Strukturerhalt
  - JSON-Kanonisierung
  - Determinismus
- Regression + Benchmarking:
  - `eval/datasets/multimodal_regression.jsonl`
  - `ntf_multimodal_benchmark.py`
  - persistierbare Reports in `eval/results/`
- CI-Absicherung:
  - `.github/workflows/multimodal-ci.yml` (Tests + Benchmark Artifact + Threshold Gates)
- Dataset-Ausbau:
  - zusätzliche Domänen-Datasets (`finance`, `medical`, `legal`, `code-heavy`)
- Dashboard-Readiness:
  - latest Snapshot für Site-Load unter `docs/benchmarking/multimodal_latest.json`
  - History-Track unter `docs/benchmarking/multimodal_history.json` inkl. Delta-Werten
- Skalierung Datensätze:
  - >100 Cases Baseline (`multimodal_expanded_120.jsonl`)
  - >500 Cases Expansion (`multimodal_expanded_600.jsonl`)
- CI-Härtung:
  - Python-Matrix (3.10 + 3.11) + strengere Threshold-Gates
  - Per-Case-Gates zusätzlich zu Durchschnittswerten

Nächste Iteration:
- RDF von lexical + sequence blend auf stärkere semantische Metrik (Embedding/Model-based) erweitern.
- SCS AST-aware auf weitere Sprachen ausbauen.
- SSR auf kontextsensitives Risk-Scoring mit weniger Regex-Approximation vertiefen.

---

## 6) Risiko- und Realitätscheck

- 98% Verarbeitung + 99% Rekonstruktion sind erreichbar als Engineering-Target,
  aber nur mit klaren Datenklassen, robustem Containerformat, harter Testabdeckung
  und iterativer Korpuserweiterung.
- Ein reiner Keyword-Folding-Ansatz reicht nicht aus; nötig ist eine hybride Architektur aus Semantik-, Struktur- und Integritätskomponenten.
