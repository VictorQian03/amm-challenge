# apr21-screen490-1431 rounds 16-20

Run index: [apr21-screen490-1431.md](apr21-screen490-1431.md)

## Round 16: New Upstream Topology After Route/OOB/Inventory Saturation

### Starting State

- Official incumbent: `screen_0001` at `485.92377070367183`.
- Best retained raw discard: `screen_0002` at `486.15826964779`.
- Breakout target: `490`.
- Latest support-only positive anchor: `CappedLeakageRebateSuppression` at `+0.010387304826565469`.
- Latest rejected seams:
  - OOB short-gap and OOB inventory recombinations
  - elapsed-gap over-tightening
  - route-quality hazard retry
  - pure flow cross-memory reduction

### Round 16 Search Constraints

- Keep layer 5/6 at zero for the first Round 16 batch.
- Do not use OOB, route/gap hazard, typed export recapture ownership, burst admission, or inventory overlay motifs.
- Import at least two genuinely new upstream/topology ideas instead of polishing Round 14/15 near misses.
- Any support use of `CappedLeakageRebateSuppression` must stay isolated and cannot be stacked with another small anchor in the same probe.

### Pre-Review Draft Probe Plan

- `SignedImpactConsistencyClassifier`
  - Layer mutation: layer 1 trade-direction observation into layer 3 hazard classification
  - Interface boundary: add hazard evidence only when trade direction, observed price movement, and latent divergence agree; do not change calm memory, flow memory, spread, side protection, or opportunity formulas
  - Outcome target: reduce arb leakage by distinguishing directional adverse selection from benign large participation without using OOB or gap evidence
  - Explicit exclusions: no OOB participation split, no route/gap hazard, no layer 4-6 edits
- `TailCompressedObservation`
  - Layer mutation: layer 1 observation shaping only
  - Interface boundary: compress only the extreme tail of `volObservation` before hazard/calm classification; leave flow, spread, side protection, and opportunity formulas untouched
  - Outcome target: recover floor slices from over-tightened elapsed-gap/event branches while measuring whether the incumbent overreacts to rare observation tails
  - Explicit exclusions: no calm boost, no shared rebate change, no downstream protection/opportunity edits
- `ReversionHazardVeto`
  - Layer mutation: layer 3 hazard/calm classification
  - Interface boundary: use movement toward the latent spot only as a bounded hazard-veto signal; do not increase `calmMemory`, change recentering, recapture eligibility, refill, or opportunity formulas
  - Outcome target: identify benign mean-reversion states without broad quiet-state opportunity reopening
  - Explicit exclusions: no passive recapture changes, no safe-side refill changes, no inventory centering changes

### Entropy Review Request

- Ask a read-only sidecar to review before source work.
- Drop or tighten any branch that:
  - reproduces OOB participation/impact splitting
  - uses gap/route evidence under a new name
  - routes calm evidence into layer 5/6 behavior too broadly
  - creates a broad fee-band change instead of an upstream classifier test

### Entropy Review Outcome

- The sidecar accepted `SignedImpactConsistencyClassifier` as the strongest keep because signed trade-direction evidence is outside the OOB/route/gap neighborhood.
- The sidecar rejected `TailCompressedObservation` because replacing global `volObservation` would fan out into hazard, flow, event carry, spread, quiet/calm, and opportunity gates.
- `ReversionVelocityClassifier` was tightened to `ReversionHazardVeto`:
  - it may only damp hazard when price movement is converging toward latent spot
  - it must not increase calm memory or touch recentering, passive recapture, refill, inventory, or opportunity formulas

### Reviewed Round 16 Probe Plan

- `SignedImpactConsistencyClassifier`
  - Layer mutation: layer 1 trade-direction observation into layer 3 hazard classification
  - Boundary after review: bounded classifier evidence only; no `volObservation`, `flowPulse`, `eventSignal`, spread coefficient, calm, recentering, recapture, refill, inventory, or opportunity changes
- `ReversionHazardVeto`
  - Layer mutation: layer 3 hazard veto only
  - Boundary after review: damp the current hazard observation under convergence evidence; no calm boost and no downstream formula edits

### Probe Sources

- Scratch sources and JSON probe results live under:
  - `artifacts/scratch_probes/apr21-screen490-1431/round16/`
- Families explored:
  - `signed_impact_consistency_classifier.sol`
  - `reversion_hazard_veto.sol`

### Probe Results

- Signed trade-direction classifier: `SignedImpactConsistencyClassifier`
  - Mean edge: `485.92377070367183`
  - Delta vs incumbent baseline: `0`
  - Key profile: `arb_loss_to_retail_gain=0.09961822784430861`, `quote_selectivity_ratio=21.366983876018754`, `time_weighted_mean_fee=0.004662250340166877`
  - Floor slices: `low_decile_mean_edge=370.69865470550553`, `low_retail_mean_edge=415.9137203431734`, `low_volatility_mean_edge=463.32099611706855`
  - Outcome: exact no-op; the bounded signed-impact evidence did not activate enough to move the screen phenotype.
- Reversion hazard-veto classifier: `ReversionHazardVeto`
  - Mean edge: `485.0895641827317`
  - Delta vs incumbent baseline: `-0.8342065209401426`
  - Key profile: `arb_loss_to_retail_gain=0.10134707012970552`, `quote_selectivity_ratio=21.807634055602264`, `time_weighted_mean_fee=0.004647320744254235`
  - Floor slices: `low_decile_mean_edge=370.37764451813086`, `low_retail_mean_edge=415.1697287223503`, `low_volatility_mean_edge=462.5906576437133`
  - Outcome: clear discard; hazard damping on reversion evidence reopened leakage and damaged floors.

### Decision

- No Round 16 candidate earned a canonical spend.
- The retained lane remains unchanged:
  - incumbent: `screen_0001`
  - best raw non-promoted: `screen_0002`
  - best fresh upstream scratch anchor: `OrthogonalObservationBasis`
  - support-only positive anchor: `CappedLeakageRebateSuppression`

### Updated Entropy Discipline

- Treat signed-impact evidence as too weak in bounded classifier-only form; do not repeat without a stronger independent activation test.
- Treat reversion hazard damping as unsafe for now; it moved in the over-open direction and weakened floor slices.
- Round 17 should not spend on scalar hazard dampers or small classifier evidence terms alone. The next batch needs either:
  - a new external topology, or
  - a structural separation that changes the interface contract rather than another small additive classifier term.

### Round 17 Starting Constraints

- Do not spend on another small additive classifier term, scalar hazard damper, route/gap hazard, OOB participation split, flow-memory ownership tweak, or layer 5/6 inventory/recapture branch.
- Require at least one idea imported from outside the current strategy's local vocabulary before source work.
- Prefer a structural interface change with clear ownership, such as:
  - an explicit two-channel hazard representation where adverse-selection protection and benign-flow fee capture consume different bounded signals
  - a seed- or regime-conditioned estimator that changes only observation interpretation, not downstream spread/protection formulas
  - a benchmark-relative normalizer anticipation signal that remains upstream and does not directly change layer 5/6 opportunity
- Keep `CappedLeakageRebateSuppression` as a support-only control and do not combine it until a larger primary anchor exists.
