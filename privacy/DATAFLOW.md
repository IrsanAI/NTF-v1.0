# MindMaster Dataflow (Phase 0 skeleton)

1. User authorizes source (e.g., Grok export channel).
2. Connector orchestrator pulls ToS-compliant payloads.
3. Data vault encrypts records (AES-256-GCM + wrapped DEK).
4. RAG pipeline derives embeddings/NTF summaries with redaction.
5. UI renders diffs + skill-tree state.
