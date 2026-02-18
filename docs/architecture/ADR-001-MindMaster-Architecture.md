# ADR-001 — MindMaster Architecture (Phase 0/1)

- **Status:** Proposed
- **Date:** 2026-02-18
- **Decision Makers:** Repo Maintainers + Agent Contributors

## Context
The repository intent is NTF-first: semantic compression, measurable quality, and future A2A optimization. Blueprint v2 proposes a browser-first, local-first DSGVO architecture with strict guardrails.

## Decision
For Phase 0/1 we adopt a **local Docker Compose architecture** with four services:
1. `mindmaster-web` (browser UX)
2. `mindmaster-core` (orchestration, policies, NTF-aware processing)
3. `mindmaster-vault` (encrypted persistence boundary)
4. `mindmaster-worker` (scheduled connector pulls, bounded jobs)

Public API exposure is intentionally deferred. Local UI + local services are the only runtime path in MVP.

## Consequences
### Positive
- Fast onboarding for humans and later agents (single compose command).
- Better security posture via strict local boundaries.
- Measurable MVP path aligned with NTF metrics (INTFR + drift checks).

### Negative / Trade-offs
- Initial setup complexity (multiple containers vs single script).
- Some features (autonomous A2A) deferred by policy.

## Guardrails
- One provider first (Phase 1).
- No autonomy before audit.
- Security before spectacle.

## Related
- `docs/architecture/THREAT_MODEL.md`
- `MINDMASTER_PROXY_BLUEPRINT.de.md`
