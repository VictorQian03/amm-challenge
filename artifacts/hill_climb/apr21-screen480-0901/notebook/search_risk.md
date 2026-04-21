# Search Risk

## Mutation Families

- depth_normalized_imbalance_router [UNPROVEN risk, fragility=0.00]: 0/0 survivors; last status none
- fill_value_admission_budget [UNPROVEN risk, fragility=0.00]: 0/0 survivors; last status none
- queue_imbalance_fair_mid [UNPROVEN risk, fragility=0.00]: 0/0 survivors; last status none
- queue_rank_protection_budget [UNPROVEN risk, fragility=0.00]: 0/0 survivors; last status none

## Primary Layers

- opportunity_budget [UNPROVEN risk, fragility=0.00]: 0/0 survivors
- quote_map [UNPROVEN risk, fragility=0.00]: 0/0 survivors
- risk_budget [UNPROVEN risk, fragility=0.00]: 0/0 survivors
- state [UNPROVEN risk, fragility=0.00]: 0/0 survivors

## Fair-Mid / State Estimation

- state [UNPROVEN risk, fragility=0.00]: 0/0 survivors
- Recorded fair-mid/state branches: queue-imbalance-fair-mid
- Treat `state` as fair-mid estimation first: name the latent/fair mid, how it updates, when it recenters, and how quote logic consumes divergence from that estimate.

## External Ideas / Web Search

- External ideas seen: depth_normalized_order_flow_imbalance, latency_screened_fill_value, microprice_queue_imbalance, queue_position_inventory_risk
- For new idea batches, do explicit web searches for market-making, inventory-control, adverse-selection, and microstructure concepts that are absent from the exhausted batch, then record the hook in `novelty_coordinates.external_idea` and the sources in `research_refs`.
