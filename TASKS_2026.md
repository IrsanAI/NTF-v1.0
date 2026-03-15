# NTF-v1.0 Task Board (Execution Track)

## Done
- [x] Roadmap/Status-Analyse erstellt (`ROADMAP_ANALYSE_2026.md`)
- [x] GitHub Page modernisiert (FluxLab + DSGVO Workflow + Validator)
- [x] Lizenz ergänzt (`LICENSE`)
- [x] Test-Suite stabilisiert (`test_ntf_comprehensive.py` INTFR expectation)
- [x] Multimodal Pipeline in Codebasis verankert (`ntf_multimodal_pipeline.py`)
- [x] `ntf_multimodal_pipeline.py` CLI + JSON export ergänzt
- [x] Erste Metriken integriert: RDF/SCS/SSR (baseline)
- [x] Regression-Set mit Mischinputs angelegt (`eval/datasets/multimodal_regression.jsonl`)
- [x] Benchmark-Runner für Multimodal-Pipeline hinzugefügt (`ntf_multimodal_benchmark.py`)
- [x] docs/ + README um Pipeline v0.3 und Metriken ergänzt
- [x] Benchmark-Ergebnisse versioniert in `eval/results/` persistierbar gemacht
- [x] CI-Job für Multimodal-Benchmark + Roundtrip-Tests angelegt
- [x] Dashboard/Docs: automatische Anzeige der neuesten `docs/benchmarking/multimodal_latest.json`
- [x] Additional datasets für finance/medical/legal/code-heavy ergänzt
- [x] CI-Threshold Gates (avg RDF/SCS/SSR Mindestwerte) aktiviert
- [x] Zeitreihen-Dashboard-Basis (History JSON + UI Anzeige der letzten Runs)
- [x] Dataset-Coverage auf >100 Cases erweitert (`multimodal_expanded_120.jsonl`)
- [x] CI-Matrix für mehrere Python-Versionen aktiviert
- [x] Drift-Analyse: automatische Delta-Berechnung zwischen History-Runs
- [x] Dataset-Coverage auf >500 Cases erweitert (`multimodal_expanded_600.jsonl`)
- [x] CI Quality Gates um Per-Case Floor-Werte ergänzt

## In Progress
- [ ] Realistische RDF-Variante mit stärkerer Semantikkomponente (Embedding/Model-based)
- [ ] SCS erweitern (AST-aware checks über Python hinaus)
- [ ] SSR erweitern (kontextsensitives Risk-Scoring statt Regex/Marker-only)

## Next (highest priority)
- [ ] Delta-Drift visualisieren (Sparkline/Chart statt Tabelle)
- [ ] Dataset-Coverage auf >1000 Cases ausbauen
- [ ] Quality-Gates pro Domänen-Dataset differenzieren

## Later
- [ ] MindMaster Connector produktivisieren (official export adapters)
- [ ] Data-Vault KMS/HSM Integration
- [ ] Multi-hop A2A Drift-Control in Simulation
