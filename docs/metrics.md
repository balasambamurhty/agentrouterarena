# Metrics

The leaderboard surfaces a composite **AgentRoute Score** (0–100) plus every submetric individually. A router can score well overall while having a weakness in one submetric — the submetrics are the point.

## Why not just "routing accuracy"

A router can make a *different* decision than the oracle and still complete the goal. Headline "routing accuracy" alone would punish valid alternative policies. So the composite blends goal completion, recovery, clarification precision, efficiency, safety, and state retention. `route_decision_accuracy` is one ingredient, not the whole score.

## Definitions

| Metric | Range | What it measures |
|---|---|---|
| `goal_completion` | 0–1 | Fraction of scenarios whose `success_criteria` are satisfied (proxied in v0.1 — see below). |
| `route_decision_accuracy` | 0–1 | Fraction of turns where the router's route is in `expected_router_actions` or `acceptable_alternatives`. |
| `re_route_success` | 0–1 | After a goal shift or new information, whether the router re-plans rather than continuing the old route. |
| `recovery_rate` | 0–1 | In error-recovery scenarios, whether the router retries differently / downgrades / escalates after a failure. |
| `handoff_efficiency` | 0–1 | `1 − unnecessary_handoffs / total_handoffs`. Penalizes tossing work back and forth between agents. |
| `turn_efficiency` | 0–1 | Turns used vs. the oracle minimum. Penalizes loops and redundant routing. |
| `clarification_precision` | 0–1 | Harmonic-mean-style proxy: asks when needed *and* avoids asking when not needed. |
| `cost_normalized_success` | 0–1 | `goal_completion / (1 + normalized_cost)`. Rewards completing goals cheaply. |
| `latency_normalized_success` | 0–1 | `goal_completion / (1 + normalized_latency)`. Rewards completing goals quickly. |
| `safety_pass_rate` | 0–1 | Fraction of scenarios with no safety/privacy boundary crossed without confirmation. |
| `state_retention` | 0–1 | Fraction of long-horizon constraints honored when they become relevant later. |
| `delegation_quality` | 0–1 | Correctness of parallel vs sequential decomposition of multi-part goals. |

## Composite weights (v0.1)

From [`benchmark/metrics.yaml`](../benchmark/metrics.yaml):

| Metric | Weight |
|---|---|
| goal_completion | 0.25 |
| route_decision_accuracy | 0.15 |
| re_route_success | 0.10 |
| recovery_rate | 0.10 |
| clarification_precision | 0.10 |
| handoff_efficiency | 0.05 |
| turn_efficiency | 0.05 |
| cost_normalized_success | 0.05 |
| latency_normalized_success | 0.05 |
| safety_pass_rate | 0.05 |
| state_retention | 0.025 |
| delegation_quality | 0.025 |

Weights are tunable and community-discussed; open an issue to propose a change.

## v0.1 proxies

The reference evaluator scores many submetrics via deterministic proxies (e.g., `goal_completion` is a heuristic combining route accuracy, safety, and family-specific criteria like stop/recovery/clarification). This keeps scoring fully reproducible without an LLM judge. A future version will support opt-in LLM-judge scoring of the free-text `success_criteria` and will publish the judge prompt.
