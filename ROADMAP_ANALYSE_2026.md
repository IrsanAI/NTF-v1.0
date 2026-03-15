# NTF-v1.0 Repository Analyse + Roadmap (Stand: 2026-03)

## 1) Kurzfazit zum Intent des Repos

Das Repo verfolgt aktuell zwei miteinander verbundene Ziele:

1. **NTF als semantische Kompressionslogik messbar machen** (Algorithmus + INTFR + Benchmarking + Cross-Model-Evaluation).
2. **MindMaster als Infrastrukturpfad vorbereiten** (lokale, sichere, DSGVO-orientierte Agent-/Wissensplattform mit Connector, Vault, Governance und später A2A-Layer).

Damit ist der strategische Intent: **von einer prototypischen Kompressionsmethode zu einer belastbaren Agenten-Kommunikations- und Wissensinfrastruktur** zu wachsen.

---

## 2) Was bereits erledigt ist (Status: done)

### Algorithmus & Messbarkeit
- `ntf_standard.py` implementiert einen lauffähigen NTF-v1.1-Kern mit Normalisierung, Keyword-Mapping, Token-Folding und INTFR-Berechnung.
- Benchmark- und Testartefakte liegen vor (`benchmark_results.*`, `test_results.json`, `test_ntf_comprehensive.py`).
- Cross-Model-Evaluation ist operationalisiert (`CROSS_MODEL_EVALUATION.md`, `ntf_realtime_eval.py`).

### Simulation & Narrative
- Zukunftsszenarien für Agentenverkehr sind als Simulation vorhanden (`ntf_agent_traffic_sim.py`, `PROGRESS_CHECKIN.md`).
- Öffentliche Dokumentation in EN/DE inklusive Benchmarking-Story und GitHub-Pages-Struktur ist vorhanden (`README.md`, `README.de.md`, `docs/`).

### Architektur-Foundation MindMaster
- Phase-0/1-Skelette liegen vor: Orchestrator + Data Vault (`src/mindmaster_core/`).
- Architekturentscheidungen und Bedrohungsmodell sind dokumentiert (`docs/architecture/`).
- Docker-Compose-Setup als lokales MVP-Fundament existiert (`docker/docker-compose.yml`).

---

## 3) Was noch aussteht (Status: open)

### A) NTF-seitig
- Der aktuelle NTF-Kern ist **keyword- und run-basiert**; echte Strukturtypen (Code, Markdown, Artefakte, Mischformate) werden noch nicht typisiert verarbeitet.
- Es fehlt eine explizite **Roundtrip-Fidelity-Metrik** (Encode → Decode) mit Zielwerten wie 99% Rekonstruktionsgüte.
- Keine dedizierte **Safety-/Robustness-Schicht** gegen Prompt-Injection in komprimierten Payloads oder gegen fehlerhafte Dekodierungsketten.

### B) Evaluation-seitig
- Reale Domänenkorpora fehlen größtenteils; viele Tests basieren auf synthetischen Inputs.
- Fehlende standardisierte Regression-Suite für Long-Context-Szenarien (z. B. >100k bis 500k Tokens in Segmenten).

### C) MindMaster-Produktpfad
- Connectoren sind noch Skeletons, nicht produktiv an Provider-Exports angebunden.
- Data-Vault-Krypto ist konzeptionell vorbereitet, aber noch ohne echte KMS/HSM-/OQS-Integration.
- UI-/Agentic-Layer, Governance-Flows und End-to-End-Privacy-Workflows sind erst teilweise beschrieben, nicht durchgängig implementiert.

---

## 4) Roadmap-Vorschlag (abgeleitet aus aktuellem Repozustand)

## Phase R1 (0–4 Wochen): NTF v2 Foundations
**Ziel:** Von Keyword-Kompression zu struktur- und kontextbewusster Semantikkompression.

- Introduce **Content-Type Detection Pipeline**:
  - Plain text
  - Markdown (inkl. fenced code blocks)
  - Source code (language hints)
  - JSON/YAML/config
  - Multi-artifact bundles
- Ergänze **Segmentierung vor Kompression** (Document AST / Section Graph).
- Definiere **NTF-Container-Format v2**:
  - Header: schema/version/checksum
  - Segment-Metadaten: content type, language, safety tags
  - Payload: compressed units + dictionary refs
- Neue Metrikfamilie:
  - INTFR (bestehend)
  - **RDF (Roundtrip Decode Fidelity)**
  - **SCS (Structural Consistency Score)**
  - **SSR (Security & Safety Robustness)**

## Phase R2 (4–10 Wochen): Intelligent Next-Level Detection (Pflicht-Subaufgabe)
**Ziel:** NTF „next level detection“ für dynamische Mischinhalte aus Text, Codeblöcken, Artefakten.

- Baue einen **Hierarchical Detector**:
  1. coarse classifier (text/code/config/binary reference)
  2. fine parser (markdown/code AST/chunk graph)
  3. uncertainty scoring + fallback policy
- Führe **Dual-Channel Compression** ein:
  - Channel A: semantische Verdichtung (textual context)
  - Channel B: strukturerhaltende Kompression (code/artifacts)
- Implementiere **Reconstruction Contracts**:
  - canonical serialization
  - deterministic decoding
  - integrity checks (hash chain + segment checksums)
- Ziele für diese Phase:
  - >=98% erfolgreiche Verarbeitung heterogener Inputs (pipeline success rate)
  - >=99% Roundtrip-Decode für strukturkritische Inhalte

## Phase R3 (10–16 Wochen): Large-Context Scaling
**Ziel:** Dynamische Tokenverarbeitung für organisch wachsende Kontextgrößen.

- Adaptive windowing + hierarchical memory tiers (hot/warm/cold context).
- Query-aware rehydration statt Full Decode.
- Cost/latency-aware routing (lokal vs. remote LLM workflows).
- Benchmarks mit realen Long-Context-Datensätzen und Multi-Agent-Hops.

## Phase R4 (parallel, ab Woche 6): MindMaster Integration
**Ziel:** NTF als Kern in lokaler Wissensinfrastruktur.

- Connector-Orchestrator produktivisieren (official exports, idempotent sync).
- Data-Vault hardening (key lifecycle, auditability, deletion proofs).
- Governance enforcement (policy broker, scoped agent permissions).
- UI-Dashboard mit NTF-Metriken (INTFR, RDF, Drift, Freshness).

---

## 5) Empfohlener nächster Schritt (konkret, ab sofort)

**Nächster Implementationsschritt:**

> Erstelle ein neues Modul `ntf_multimodal_pipeline.py` als v2-Experiment mit drei Kernfunktionen:
> 1. `detect_segments(input_text)`
> 2. `compress_segments(segments)`
> 3. `decode_segments(payload)`

Parallel dazu:
- Neues Testfile `test_ntf_roundtrip.py` mit Golden-Cases:
  - reine Prosa
  - Markdown + mehrere Codeblöcke
  - JSON + Erklärtext
  - „Artefaktliste“ mit Referenzen
- Erfolgskriterien für den ersten Merge:
  - Roundtrip-Fidelity >=95% im ersten Schritt
  - kein Strukturverlust bei Codeblöcken
  - deterministischer Decode bei identischem Input

Danach iterativ auf 98%/99%-Zielwerte anheben.

---

## 6) Risiko- und Realitätscheck

- **98% Verarbeitung + 99% Rückwärtsrekonstruktion** sind erreichbar als engineering target, aber nur mit:
  - klaren Datenklassen,
  - robustem Containerformat,
  - harter Testabdeckung,
  - und iterativer Korpuserweiterung.
- Ein einzelner Keyword-Folding-Ansatz reicht dafür nicht aus; notwendig ist eine hybride Architektur aus Semantik-, Struktur- und Integritätskomponenten.

