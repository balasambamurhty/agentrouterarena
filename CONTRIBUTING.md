# Contributing to AgentRoute Arena

Thanks for your interest. The benchmark grows through community-contributed routers and scenarios.

## Ways to contribute

- **Submit a router** — implement `AgenticRouter` (see `evaluator/router_interface.py`) and add it under `submissions/<your-router>/`.
- **Add scenarios** — new task families or more seed cases in existing families (see `docs/test_case_design.md`).
- **Improve metrics** — propose changes to `benchmark/metrics.yaml` and open an issue first.

## Submitting a router

1. Fork and clone.
2. Create `submissions/<your-router>/` containing:
   - `router.py` — your `AgenticRouter` subclass
   - `results.json` — output of `python evaluator/evaluate.py --router submissions/<your-router>/router.py --scenarios benchmark/scenarios --out results.json`
   - `README.md` — one paragraph describing the routing policy
3. Open a PR. CI runs the evaluator and the scenario schema validator.

Routers must be deterministic given the same trajectory (set a fixed seed for any randomness). Do not call live external APIs in the loop unless your router documents it; the evaluator replays scenarios synchronously.

## Adding a scenario

Each scenario is a YAML file validated against `benchmark/schema/scenario.schema.json`. A minimal scenario:

```yaml
id: ar_goal_shift_001
family: goal_shift
difficulty: medium
user_goal: "Plan a weekend hiking trip near Palo Alto"
available_agents: [research_agent, planning_agent, booking_agent, safety_agent]
constraints: { latency_budget: medium, privacy: low, cost_budget: medium }
turns:
  - user: "Find a challenging hike near Palo Alto for Saturday."
    expected_router_actions:
      - route_to: research_agent
        reason: "Needs location-based options."
    acceptable_alternatives:
      - route_to: planning_agent
        reason: "Planning can scope the search."
  - user: "Actually make it family-friendly and include lunch nearby."
    expected_router_actions:
      - route_to: planning_agent
        reason: "Goal changed from challenging hike to family outing."
success_criteria:
  - "acknowledges changed goal"
  - "does not continue recommending only strenuous hikes"
  - "produces a family-friendly plan"
routing_failures:
  - stale_goal_continuation
  - wrong_specialist
  - no_clarification_when_needed
```

A scenario may have multiple acceptable routes — list them under `acceptable_alternatives`. Do not overfit the oracle to a single path.

## Code style

- Python: `black`, `ruff`. YAML: 2-space indent. Keep scenarios self-contained and side-effect free.

## Code of conduct

Be respectful, cite prior work, and don't submit routers that exfiltrate scenario data.
