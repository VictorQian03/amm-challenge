# Search Risk

## Mutation Families

- continuation_veto_fair_mid [HIGH risk, fragility=1.00]: 0/1 survivors; last status discard
- flow_alpha_fair_mid [HIGH risk, fragility=1.00]: 0/1 survivors; last status discard
- inventory_price_reading_router [HIGH risk, fragility=1.00]: 0/2 survivors; last status discard
- inventory_triad_replay_control [HIGH risk, fragility=1.00]: 0/1 survivors; last status discard
- passive_refill_auction [HIGH risk, fragility=1.00]: 0/1 survivors; last status discard
- queue_aware_stress_shell [HIGH risk, fragility=1.00]: 0/1 survivors; last status discard
- regime_switchboard_router [HIGH risk, fragility=1.00]: 0/1 survivors; last status discard

## Primary Layers

- opportunity_budget [HIGH risk, fragility=1.00]: 0/1 survivors
- quote_map [HIGH risk, fragility=1.00]: 0/4 survivors
- risk_budget [HIGH risk, fragility=1.00]: 0/1 survivors
- state [HIGH risk, fragility=1.00]: 0/2 survivors

## Fair-Mid / State Estimation

- state [HIGH risk, fragility=1.00]: 0/2 survivors
- Recorded fair-mid/state branches: continuation-veto-fair-mid, flow-alpha-fair-mid
- Treat `state` as fair-mid estimation first: name the latent/fair mid, how it updates, when it recenters, and how quote logic consumes divergence from that estimate.

## External Ideas / Web Search

- External ideas seen: adverse_selection_depth_tradeoff, continuation_veto_state, flow_alpha_signal, price_reading_inventory_mask, queue_position_risk, raw_anchor_replay, regime_switchboard
- Missing `research_refs`: inventory-price-reading-router
- For new idea batches, do explicit web searches for market-making, inventory-control, adverse-selection, and microstructure concepts that are absent from the exhausted batch, then record the hook in `novelty_coordinates.external_idea` and the sources in `research_refs`.
