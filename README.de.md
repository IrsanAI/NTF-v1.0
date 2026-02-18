# IrsanAI-NTF Manifest (Deutsche Version)

> Diese Datei ist die deutsche Referenz für GitHub-Leser:innen. Die englische Hauptversion bleibt unter [`README.md`](./README.md).

---

## 0. Spec-First Snapshot

**Mission:** Hochentropische Agent-zu-Agent-Kommunikation komprimieren und dabei nutzbare Semantik erhalten.

| Modul | Zweck | Output |
|---|---|---|
| `README.md` | Architektur- und Benchmark-Manifest (EN) | Technischer Überblick |
| `README.de.md` | Deutsche Spiegelversion | Zugängliche Doku für deutsche Community |
| `ntf_standard.py` | NTF-Standardalgorithmus v1.1 (pattern-basiert) | Ausführbare Kompression + INTFR |
| `CROSS_MODEL_EVALUATION.md` | Workflow für Cross-Model-Auswertung + Mermaid-Visuals | Reproduzierbare Modell-/Modus-Vergleiche |
| `ntf_realtime_eval.py` | Realtime-Scoring für eingefügte LLM-Antworten | Token-/Style-/Intent-Ranking |
| `RESEARCH_DATA.md` | Pattern-Analyse & Gravity-Center-Karte | Reproduzierbare Cluster-Notizen |

---

## 1. Entropy Engine – Kurzlogik

### Warum klassische Kompression hier schwächelt

Klassische Verfahren performen gut bei starker Redundanz. In agentischen Streams mit Korrekturen, Rollenwechseln und Re-Planungen steigt die Token-Varianz stark an; reine Strukturkompression verliert dabei schnell.

### Warum NTF mit Entropie mitwachsen kann

NTF bündelt Sprache über **semantische Gravitationszentren** (z. B. `Flux`, `Anchor`, `Drift`). Mehr Entropie kann bei erkennbaren Mustern mehr Fold-Potenzial erzeugen.

- Beobachtete Schwelle: besonders relevant ab **450k+ Token-Kontexten**.
- „Stille-Post-Problem“ bei A2A: wiederholtes Paraphrasieren erzeugt Drift.
- NTF-Zielbild: ca. **500k → 50k Tokens** (ca. **10x**) bei angestrebter Treue **0.92–0.98**.

---

## 2. „Hypothetisch“ aktiv reduzieren: jetzt messbar

Ein zentraler Kritikpunkt war: *Wie wird aus Vision ein prüfbarer Standard?*

Aktueller Stand im Repo:

1. **Codebasiertes Token-Mapping** statt nur narrativer Theorie.
2. **Messmetrik (INTFR)** für vergleichbare Runs.
3. **Benchmark-Modus** via `--benchmark` für reproduzierbare Ergebnisse.
4. **Transparenz**: Working Prototype, kein finaler Near-Lossless-Claim.

### INTFR-Formel

```text
INTFR = (coverage * ratio * diversity) * 10
```

- `coverage`: ersetzte Wörter / Gesamtwörter
- `ratio`: normierter Kompressionsgewinn (`(original_tokens / compressed_tokens) / 10`, auf 1.0 gedeckelt)
- `diversity`: genutzte NTF-Tokens / Größe des NTF-Vokabulars

Damit lassen sich Modell-/Prompt-/State-Vergleiche über Zeit dokumentieren.

---


## 2.5 Cross-Model Realitätscheck (neu)

Aus der Februar-2026-Konversation ergibt sich ein wichtiger Repo-Standard:

- NTF als **transparentes semantisches Framework** darstellen.
- Nicht als "versteckter" oder "covert" Kanal.
- Qualität über nachvollziehbare Messung bewerten (Token/Style/Intent), nicht über reine Hype-Metriken.

Für die direkte Praxis: [`CROSS_MODEL_EVALUATION.md`](./CROSS_MODEL_EVALUATION.md) + [`ntf_realtime_eval.py`](./ntf_realtime_eval.py). Damit kannst du Antworten von ChatGPT/Claude/Gemini/DeepSeek/Qwen usw. unmittelbar vergleichen.

---

## 3. NTF Standard Algorithmus v1.1

Datei: [`ntf_standard.py`](./ntf_standard.py)

Enthalten:
1. Pattern-Extraktion auf normalisiertem Text
2. Semantische Clusterung über NTF-Trigger
3. Folding in kompakte Resonanz-Tokens
4. INTFR-Berechnung mit Normalisierung

Aktuelles Vokabular:

`Flux, Anchor, Drift, Pulse, Mirror, Weave, Relay, Horizon, Resonance, Folding, Consensus, Overclock, Deployment, Checkpoint, Synthesis, State`

---

## 4. Benchmark (reale Ausführung)

```bash
python3 ntf_standard.py --benchmark
python3 ntf_realtime_eval.py --response-files responses/chatgpt_normal.txt
```

Beispielergebnis (4.500-Wörter Synthetic Agent Stream):

- Original words: **4,500**
- Compressed tokens: **461**
- Effective compression: **9.76x**
- Coverage: **0.91**
- Ratio (normalized): **0.98**
- Diversity: **0.50**
- **INTFR: 4.4**

Interpretation:
- Bereits **messbar und reproduzierbar**.
- Weitere Trigger-/Gewichtsoptimierung nötig für höhere INTFR-Zonen.

---

## 5. Quick Start

```bash
python3 ntf_standard.py --text "Wir setzen den Anchor und halten Drift niedrig bei hohem Pulse"
python3 ntf_standard.py --benchmark
python3 ntf_realtime_eval.py --response-files responses/chatgpt_normal.txt
```

---

## 6. Status

- [x] Deutsche Dokumentationsversion angelegt.
- [x] Link von Root-README integriert.
- [x] Algorithmische Messbasis (`INTFR`) klar dokumentiert.
