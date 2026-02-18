# MindMaster Threat Model (Phase 0)

## Scope
- Local browser-first deployment
- Connector-based import from official export/legal access paths
- Encrypted local vault + RAG index + agent runtime (bounded)

## STRIDE Analysis

| Category | Example Threat | Impact | Mitigations | Owner |
|---|---|---|---|---|
| Spoofing | Stolen browser session cookie | Unauthorized data access | WebAuthn/device binding, short TTL, rotate session keys | web/core |
| Tampering | Manipulated chat export file | Poisoned memory graph | Signature/hash verification, append-only audit hash chain | core/vault |
| Repudiation | User/agent denies an action | Forensic ambiguity | Signed event logs + trusted timestamps | core |
| Information Disclosure | PII leakage from vector index | DSGVO breach | Field-level encryption, PII redaction before embedding, strict RBAC | vault/core |
| Denial of Service | Sync loops overload provider/local worker | Service instability | Global/provider rate limits, backoff+jitter, queue budget caps | worker/core |
| Elevation of Privilege | Agent escalates from readonly to operator | Unauthorized automation | Policy broker, scoped tokens, approval gates, least privilege roles | agent/core |

## LINDDUN Privacy Mitigations

| Privacy Risk | Example | Mitigation |
|---|---|---|
| Linkability | Cross-provider profile stitching | Pseudonymous tenant IDs, per-source namespace partition |
| Identifiability | Sensitive user directly inferable | PII minimization and deterministic redaction pipeline |
| Non-repudiation (privacy concern) | Overly permanent identifiable trails | Retention policy + selective log anonymization |
| Detectability | Presence of a sensitive chat detectable | Encrypted metadata envelopes and access-controlled indexes |
| Information Disclosure | Raw transcript leaks | Envelope encryption, key isolation, encrypted backups |
| Unawareness | User unaware of data use | Explicit consent templates, in-app transparency pages |
| Non-compliance | Missing delete/export rights | One-click export/delete + verification report |

## Post-Quantum Security Strategy (Pragmatic)
- Bulk data encryption remains AES-256-GCM for performance.
- Key exchange/signature path is hybrid-ready:
  - KEX: X25519 + ML-KEM (Kyber family)
  - Signatures: Ed25519 + ML-DSA (Dilithium family)
- Crypto-agility policy supports `legacy`, `hybrid`, `pqc_strict` modes.

## Immediate Phase-0 Actions
1. Threat review walkthrough against all new services.
2. Abuse case tests for sync loops, malformed exports, role escalation.
3. Policy test checklist before enabling Phase-1 updates.
