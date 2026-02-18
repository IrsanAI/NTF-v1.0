# IrsanAI MindMaster — DSGVO-First Blueprint v2 (Human + Agent Ready)

## Aktueller Repo-Status & nächste konkrete Schritte

**Status:** Phase-0-Artefakte sind jetzt als erste Code-/Dokustruktur im Repo angelegt, damit der Übergang von Blueprint → MVP umsetzbar ist.

### Neue Struktur (Phase 0 + Phase 1 MVP)

```text
.
├── docs/architecture/
│   ├── ADR-001-MindMaster-Architecture.md
│   └── THREAT_MODEL.md
├── privacy/
├── docker/
│   ├── docker-compose.yml
│   ├── .env.example
│   └── profiles/local/
├── src/mindmaster_core/
│   ├── connector_orchestrator.py
│   └── data_vault.py
├── src/mindmaster_web/
│   ├── components/
│   ├── pages/
│   └── assets/
├── src/mindmaster_agent/
└── eval/
```

### Konkrete nächste Schritte
1. ADR und Threat Model im Team reviewen: [`docs/architecture/ADR-001-MindMaster-Architecture.md`](./docs/architecture/ADR-001-MindMaster-Architecture.md), [`docs/architecture/THREAT_MODEL.md`](./docs/architecture/THREAT_MODEL.md).
2. Lokales Compose-MVP starten: [`docker/docker-compose.yml`](./docker/docker-compose.yml) + [`docker/.env.example`](./docker/.env.example).
3. Core-Skelette iterieren: [`src/mindmaster_core/connector_orchestrator.py`](./src/mindmaster_core/connector_orchestrator.py), [`src/mindmaster_core/data_vault.py`](./src/mindmaster_core/data_vault.py).
4. Privacy- und Eval-Artefakte in `privacy/` und `eval/` als nächste PRs konkretisieren.

---

## 1) Intent-Fit: Warum passt das zum aktuellen Repo?

Das bestehende Repo verfolgt bereits denselben Kern:
- **Semantische Verdichtung (NTF)** statt blindes Token-Wachstum.
- **Messbarkeit** über klare Scores statt Hype.
- **A2A-Zukunftsfähigkeit** durch Simulations- und Evaluationspfade.

Diese Vision erweitert den Kern logisch von "Kommunikationskompression" zu einer **Wissenssouveränitäts-Plattform**:
1. User holen eigene LLM-Dialogdaten kontrolliert zurück.
2. Daten werden lokal geschützt gespeichert und semantisch strukturiert.
3. Wissen wird als persönlicher, updatefähiger Agent nutzbar.
4. Später interagieren autorisierte Agenten kontrolliert miteinander.

Kurz: **NTF wird vom Algorithmus zur Infrastruktur.**

---

## 2) Genial vs. Katastrophe: klare Entscheidung

### Genial, wenn …
- Scope strikt phasenweise begrenzt wird (MVP zuerst).
- Security/Privacy *vor* Features priorisiert wird.
- Anbieterintegrationen robust und fair laufen (Rate Limits, Consent, ToS-konform).
- Entscheidungen über messbare Metriken bewertet werden (INTFR, Retrieval-Qualität, Drift).

### Katastrophe, wenn …
- alles gleichzeitig gebaut wird (3D-UI, Multi-LLM, Agent-Netzwerk, PQC, Autonomie in v1).
- rechtliche/sicherheitstechnische Anforderungen erst „später“ kommen.
- unklare Datenflüsse zu Sicherheitslücken und Vertrauensverlust führen.

**Fazit:** Vision sehr stark, aber nur mit harter Sequenzierung + Guardrails realisierbar.

---

## 3) Zielarchitektur (Browser-first, ohne öffentliche API in v1)

### 3.1 Laufzeitmodell
- Lokales Deployment via Docker Compose (oder Podman Compose).
- Browser-Login in lokale Web-App (`https://localhost`).
- Keine offene externe API in v1; nur lokale UI + lokale Services.

### 3.2 Kernkomponenten
1. **Identity & Consent Service**
   - Login, Session-Management, Device-Bindung.
   - Einwilligung pro Datenquelle (ChatGPT/Gemini/Grok …).
   - Rollen: Owner, Readonly-Research, Agent-Operator.

2. **Connector Orchestrator (ToS-safe Pull Engine)**
   - Provider-spezifische Adapter mit offiziellen Exports/legitimen Zugriffswegen.
   - Rate-Limits pro Provider + exponentielles Backoff + Jitter.
   - Idempotenz über `sync_cursor` + `content_hash` + `message_uid`.
   - "Quiet Mode": Pulls außerhalb aktiver User-Interaktion priorisieren.

3. **Data Vault (lokal, verschlüsselt, PQ-hybrid-ready)**
   - Ruhende Daten: AES-256-GCM (DEK pro Objekt/Chunk).
   - Schlüsselhülle: Hybrid-KEX (X25519 + ML-KEM/Kyber) für KEK-Aushandlung.
   - Signaturen für Audit-Artefakte: Ed25519 + ML-DSA/Dilithium (hybrid sign).
   - Crypto-Agility-Policy (Versionierung von Algorithmen pro Datensatz).

4. **RAG & Memory Engine**
   - Chunking, Embeddings, Vektorindex, Graph-Kanten.
   - NTF-basierte Verdichtung für Langzeitwissen + Drift-Kontrolle.
   - Retrieval-Evaluation (precision/recall + temporal freshness).

5. **Persona/Agent Runtime (lokal)**
   - Simulierter "Future Agent" mit strikten Policies.
   - A2A nur bei expliziter Freigabe (Session + Scope + TTL).

6. **Visual Brain UI (WebGL-first)**
   - 3D-Brain als Wissenszustand ("aufladendes Gehirn" bei Updates).
   - Skill-Tree-Layer (kognitive Muster, Fähigkeitsknoten, Entwicklung über Zeit).
   - Diff-Overlay: Was hat sich seit letztem Sync verändert?

7. **Audit & Governance Layer**
   - Nachvollziehbare Synchronisationsereignisse.
   - One-click Export/Löschung pro Quelle (DSGVO Betroffenenrechte).
   - Policy-Hard-Stops bei Risiko-Events.

---

## 4) Security & DSGVO-by-Design (Pflicht, nicht optional)

- **Data Minimization:** nur notwendige Felder persistieren.
- **Purpose Limitation:** klare Zweckbindung je Verarbeitung.
- **Local-First Storage:** lokal als Default; Cloud nur explizit opt-in.
- **Encryption in Transit/At Rest:** TLS + starke ruhende Verschlüsselung.
- **Key Isolation:** Schlüsselmaterial strikt getrennt vom Datenspeicher.
- **Auditability:** revisionsfeste Logs für Zugriff, Sync, Löschung.
- **Right to Access/Delete:** Export + selektive Löschung pro Provider.
- **Policy Engine:** verhindert unautorisierte Agent-Aktionen und Exfiltration.

### 4.1 Threat Model (Phase-0 Pflicht: STRIDE + LINDDUN)

**STRIDE-Beispiele**
- **Spoofing:** gestohlene Session-Cookies → Mitigations: Device-Bindung, WebAuthn, kurze Session-TTL.
- **Tampering:** manipulierte Chat-Exporte → Mitigations: Signaturprüfung, Hash-Chains, Immutable-Auditlog.
- **Repudiation:** "Ich war das nicht" → Mitigations: signierte Event-Logs, Zeitstempel.
- **Information Disclosure:** PII-Leak aus Vektorstore → Mitigations: Field-Level Encryption, Zugriffspolicies.
- **DoS:** aggressive Sync-Jobs → Mitigations: Rate-Limits, Backoff, Queue-Budgets.
- **Elevation of Privilege:** Agent überschreibt User-Rollen → Mitigations: RBAC + Policy Guard + Approval Gates.

**LINDDUN-Beispiele**
- **Linkability:** Profilverknüpfung über Quellen hinweg → Pseudonymisierung + tenant-separierte IDs.
- **Identifiability:** direkte Zuordnung sensibler Inhalte → PII-Redaction vor Embedding.
- **Non-compliance:** fehlende Löschbarkeit → Löschjournal + Verifikationsreport.

### 4.2 PQC konkret ohne Performance-Kollaps

Pragmatischer Ansatz: **hybrid nur für Schlüsselmanagement/Signatur**, nicht für jeden Datenblock.

- Datenverschlüsselung bleibt schnell: AES-256-GCM (symmetrisch, hardwarebeschleunigt).
- PQC wird im Key-Envelope genutzt (KEK-Aushandlung): X25519 + ML-KEM (Kyber).
- Signatur-Hybrid nur für kritische Artefakte (Consent, Audit, Exporte).
- Crypto-Policy entscheidet algorithmisch je Client-Klasse (`legacy`, `hybrid`, `pqc_strict`).

Beispiel (Python, pseudonah):

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# libsodium/oqs-python o. ä. für Hybrid-KEX (konzeptionell)
# shared_secret = hkdf(x25519_secret || mlkem_secret)
# kek = derive_kek(shared_secret)


def encrypt_record(plaintext: bytes, dek: bytes, aad: bytes) -> tuple[bytes, bytes]:
    aes = AESGCM(dek)  # AES-256-GCM: 32-byte key
    nonce = os.urandom(12)
    ciphertext = aes.encrypt(nonce, plaintext, aad)
    return nonce, ciphertext


def wrap_dek_hybrid(dek: bytes, kek: bytes) -> bytes:
    # KEK aus Hybrid-KEX; hier symmetrisches Wrapping als Platzhalter
    aes = AESGCM(kek)
    nonce = os.urandom(12)
    return nonce + aes.encrypt(nonce, dek, b"dek-wrap-v1")
```

Lib-Empfehlungen für PoC:
- `cryptography` (AES-GCM, HKDF, klassische primitives)
- `oqs-python` (ML-KEM/ML-DSA via liboqs, experimentell)
- optional `PyNaCl`/libsodium (X25519, robuste Basiskrypto)

**Warum effizient?** AES bleibt der Datendurchsatz-Worker; PQC kostet nur bei Schlüsselaustausch/Signatur.

---

## 5) Agent-spezifische Variante (Human + Agent Dual Track)

### 5.1 Agent Login & Authorization
- Agenten erhalten **eigene Identitäten** (kein Shared User Token).
- Login via signierte Agent-Assertion + Owner-Freigabe.
- Jeder Agent-Run hat Scope (`read`, `summarize`, `propose`) + TTL.

### 5.2 Sandbox Interaktionen
- Agent Runtime in isoliertem Worker/Namespace.
- Kein direkter DB-Zugriff ohne Policy Broker.
- Tool-Aufrufe sind allowlist-basiert und auditpflichtig.

### 5.3 NTF-basierte Drift-Kontrolle
- Pro Dialog-Hop wird NTF gemessen (`INTFR`, token growth ratio, semantic coverage).
- Wenn Tokenwachstum > Schwelle oder INTFR fällt → Auto-Compression-Checkpoint.
- Eskalierende Ketten werden bei Grenzwertverletzung gestoppt.

### 5.4 Harte Guardrails für autonome A2A-Chats
- A2A nur nach expliziter User-Autorisierung (opt-in pro Session).
- Max-Hop-Limit + Max-Token-Budget pro Konversation.
- "No Autonomy before Audit": ohne vollständige Logs keine autonome Fortsetzung.

---

## 6) UX + Wissenschafts-Integration

### 6.1 Visual Brain UI (interaktiv)
- WebGL 3D-Brain: Aktivitätsknoten leuchten bei neuem Wissen.
- Update-Animation: "aufladendes Gehirn" während Sync/Indexing.
- Skill-Trees: Fähigkeiten/Interessen als wachsende Knotenpfade.

### 6.2 NTF-gekoppeltes Metrics Dashboard
- `INTFR`-Trend (Kompression/Drift über Zeit).
- Retrieval `precision/recall` pro Wissensdomäne.
- `freshness` (Zeit bis neue Inhalte im lokalen Brain verfügbar sind).

### 6.3 A/B-Tests und Feedback-Loop (3–5 Jahre)
- A/B-Test von Skill-Tree-Layouts (Verständlichkeit vs. Bedienbarkeit).
- User-Feedback nach Retrieval-Erfolg in die NTF-Optimierung zurückführen.
- Clone-Contributors liefern anonymisierte, consent-basierte Eval-Snapshots.
- Wissenschaftspfad: reproduzierbare Metrik-Reihen statt Einmal-Demos.

---

## 7) Realistische Delivery-Phasen

### Phase 0 — Fundament + Threat Model (1–2 Wochen)
- ADRs für Architektur + Crypto-Agility schreiben.
- STRIDE/LINDDUN mit Abuse-Cases und klaren Mitigations fertigstellen.
- DSGVO-Dateninventar + Consent-Flows + Löschpfade definieren.
- PQ-Hybrid-Prototyp für Key-Wrapping evaluieren (Benchmark Latenz/CPU).

### Phase 1 — MVP Local Vault (3–6 Wochen)
- Genau **ein** LLM-Connector (z. B. Grok via offiziellen Exportpfad).
- Browser-Login lokal, manueller **"Update now"**-Button.
- Diff-Ansicht: neue/aktualisierte Chats seit letztem Pull.
- Verschlüsselter Storage + Basis-RAG + NTF-Zusammenfassung.

### Phase 2 — Multi-LLM + Visual Brain (4–8 Wochen)
- Weitere Provider (ChatGPT/Gemini) in ToS-konformen Pull-Profilen.
- WebGL-3D-Brain + Skill-Tree + Dashboard.
- Evaluationsroutine für precision/recall/freshness + INTFR.

### Phase 3 — Agentic Layer (6–12 Wochen)
- Autorisierte Agent-Interaktionen in Sandbox.
- A2A-Driftkontrolle über NTF-Checkpointing + Budget-Limits.
- Stufenweise Autonomie erst nach stabilen Audit-Ergebnissen.

---

## 8) Top-3 Risiken für Scope-Explosion + Guardrails

1. **Zu frühe Multi-LLM-Integration**
   - Guardrail: erst 1 Provider stabil + auditierbar, dann sequenziell erweitern.

2. **Autonomie vor Governance**
   - Guardrail: **Keine Autonomie vor Audit** (Leitsatz).

3. **Feature-Hype vor Security-Basis**
   - Guardrail: Release-Gate verlangt Threat-Model + Encryption + Löschnachweis.

Erweiterte Leitsätze:
- "Security before Spectacle"
- "One Provider First"
- "Measured Progress over Viral Demos"

---

## 9) Antworten auf die vier Klärungsfragen

### 9.1 Wie PQC integrieren ohne Effizienzkill?
- Nicht Datenblöcke direkt PQ-verschlüsseln.
- Symmetrische Bulk-Verschlüsselung (AES-256-GCM) beibehalten.
- PQC nur für Schlüsselaustausch/Signaturen (Hybrid-KEX/Hybrid-Sign).
- Crypto-Agility per Policy, mit laufendem Benchmarking auf Consumer-Hardware.

### 9.2 Agentic Layer mit Drift-Kontrolle?
- Jeder Hop erzeugt Metrik-Checkpoint (`INTFR`, growth-ratio, intent score).
- Bei Drift-Schwelle: verdichten, zusammenfassen, weiter nur mit Budget.
- Harte Stopps bei Hop-/Token-Limit und fehlender User-Freigabe.

### 9.3 Top-3 Scope-Risiken + Gegenmittel?
- Multi-LLM zu früh, Autonomie zu früh, Security zu spät.
- Gegenmittel: sequenzierte Phasen, Audit-Gates, Security-Release-Kriterien.

### 9.4 Wie Visualisierung mit NTF koppeln?
- Skill-Tree-Knoten aus NTF-Clusterentwicklung speisen.
- 3D-Brain-Farbzustand aus Metriken (freshness, confidence, drift).
- User-Feedback ins Eval-Set zurückführen; A/B-Varianten reproduzierbar vergleichen.

---

## 10) Self-Check (1–10)

- **Machbarkeit: 8/10** — Klar phasiert, MVP realistisch mit einem Provider.
- **Eleganz: 8/10** — Security, UX und Forschung sind verbunden statt isoliert.
- **Repo-Intent-Fit: 9/10** — NTF bleibt Kernmetrik für Verdichtung und A2A-Driftkontrolle.
- **Genial-vs-Katastrophe-Verbesserung: 9/10** — Harte Guardrails senken Big-Bang-Risiko deutlich.

Kurzfazit: Gefällt mir gut, weil Security priorisiert ist und die Roadmap messbar bleibt; Phase 3 sollte konsequent schlank und audit-getrieben bleiben.

---

## Phase 0 Done Checklist

- [x] ADR für MindMaster-Architektur angelegt (`ADR-001`).
- [x] Threat Model mit STRIDE + LINDDUN als eigene Datei angelegt.
- [x] Docker-Local-Setup mit 4 Services (`web`, `core`, `vault`, `worker`) erstellt.
- [x] `.env.example` für reproduzierbare lokale Konfiguration ergänzt.
- [x] Connector-Orchestrator-Skelett mit Rate-Limit, Backoff+Jitter, Quiet-Mode erstellt.
- [x] Data-Vault-Skelett mit AES-256-GCM + PQ-hybrid-Kommentaren + Crypto-Agility erstellt.
- [x] README (EN/DE) um MVP-Startpfad erweitert.
