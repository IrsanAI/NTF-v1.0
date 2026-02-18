# RESEARCH_DATA — NTF v1.1 Pattern Analysis

## Semantic Clustering

### Observed cluster families

1. **State Stability Cluster**
   - Tokens: `Anchor`, `State`, `Checkpoint`
   - Role: preserve long-range context continuity.

2. **Temporal Dynamics Cluster**
   - Tokens: `Flux`, `Drift`, `Pulse`, `Horizon`
   - Role: track change velocity and directional futures.

3. **Coordination Cluster**
   - Tokens: `Relay`, `Consensus`, `Deployment`
   - Role: synchronize multi-agent transitions and action gates.

4. **Compression Intelligence Cluster**
   - Tokens: `Folding`, `Mirror`, `Weave`, `Synthesis`, `Resonance`
   - Role: fold semantically aligned phrases into compact representations.

5. **Performance Escalation Cluster**
   - Token: `Overclock`
   - Role: marks urgency, acceleration, and priority amplification.

## Gravity Centers

Gravity centers are high-frequency semantic anchors that attract variant wording.

| Gravity Center | Typical lexical attractors |
|---|---|
| Anchor | baseline, fixpoint, stable |
| Drift | deviation, offset, noise |
| Relay | handoff, transfer, route |
| Folding | compress, reduce, pack |
| Resonance | align, match, coherent |
| State | context, memory, status |

## Pattern Analysis Notes

- Bigrams/trigrams with repeated coordination verbs (`relay`, `merge`, `align`) produce the strongest fold opportunities.
- Entropy-heavy text improves clustering yield when terms recur as intent-level motifs.
- Effective compression depends on retaining gravity center diversity while maximizing coverage.

## Benchmark Trace (v1.1)

- Corpus size: 4,500 words
- Compression behavior: pattern-rich synthetic agent stream
- Target metric: INTFR baseline around 4.4 for normalized 4.5k benchmark


## Cross-Model Extension (Feb 2026)

To complement INTFR compression benchmarking, the repo now tracks prompt-response quality using `ntf_realtime_eval.py`.

Evaluation dimensions:
- token_match (NTF vocabulary recall)
- style (engagement and coordination language)
- intent (payload alignment)

This is intentionally separate from INTFR:
- **INTFR** measures folding/compression behavior.
- **Realtime evaluator score** measures cross-model response alignment.
