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

## In Progress
- [ ] Realistische RDF-Variante mit stärkerer Semantikkomponente (Embedding/Model-based)
- [ ] SCS erweitern (AST-aware checks über Python hinaus)
- [ ] SSR erweitern (kontextsensitives Risk-Scoring statt Regex/Marker-only)

## Next (highest priority)
- [ ] Dashboard/Docs: automatische Anzeige der neuesten `eval/results/multimodal_latest.json`
- [ ] Additional datasets für finance/medical/legal/code-heavy
- [ ] CI-Threshold Gates (fail if avg_rdf/avg_scs unter Schwellwert)

## Later
- [ ] MindMaster Connector produktivisieren (official export adapters)
- [ ] Data-Vault KMS/HSM Integration
- [ ] Multi-hop A2A Drift-Control in Simulation
