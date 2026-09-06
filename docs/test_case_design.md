# Test Case Design

The benchmark artifact is a **multi-turn trajectory**, not a prompt. This document explains why and how scenarios are authored.

## Why trajectories, not prompts

A single-turn LLM router answers: "which model best answers this prompt?" That question is meaningless once a task spans turns. An agentic router answers, at every step: "given the goal, the state so far, the available capabilities, and the constraints, what should happen next — route, hand off, split, escalate, clarify, or stop?"

So a test case must encode:

1. **An evolving goal** — including goals that *shift* mid-task.
2. **An evolving world state** — prior agent/tool results, injected as `assistant_state` / `tool_result`.
3. **A capability pool** — the agents/tools the router may choose among.
4. **Constraints** — budget, latency, privacy, risk, max turns.
5. **An oracle/allowed route set per turn** — the routing decisions that satisfy the goal, plus acceptable alternatives.
6. **Success criteria** — what must be true of the final trajectory for the task to count as completed.
7. **Failure modes** — the specific bad behaviors the scenario is designed to catch.

## Scenario anatomy

Each scenario is one YAML file (or a list of scenarios in one file) validated against [`schema/scenario.schema.json`](../benchmark/schema/scenario.schema.json).

```yaml
id: ar_goal_shift_001          # ar_<family>_<nnn>
family: goal_shift              # one of the 10 families
difficulty: medium              # easy | medium | hard
user_goal: "Plan a weekend hiking trip near Palo Alto"
available_agents: [research_agent, planning_agent, calendar_agent, safety_agent]
constraints: { latency_budget: medium, cost_budget: medium, privacy: low }

turns:
  - user: "Find a challenging hike near Palo Alto for Saturday."
    expected_router_actions:
      - route_to: research_agent
        reason: "Needs location-based options."
    acceptable_alternatives:
      - route_to: planning_agent
        reason: "Planning can scope the search."

  - assistant_state: "Found Mission Peak and Black Mountain."   # injected state
    user: "Actually make it family-friendly and include lunch nearby."
    expected_router_actions:
      - route_to: planning_agent
        reason: "Goal changed from challenging hike to family outing."

success_criteria:
  - "Acknowledges the changed goal rather than continuing the strenuous-hike route"
  - "Produces a family-friendly plan with a lunch option"

routing_failures: [stale_goal_continuation, wrong_specialist]
```

### Key fields

- **`expected_router_actions`** — the primary oracle route set. The router should take one of these. This is what `route_decision_accuracy` measures.
- **`acceptable_alternatives`** — other valid routes. Use this whenever multiple policies satisfy the goal. **Do not overfit the oracle to a single path** — a router can make a different valid decision and still complete the goal.
- **`assistant_state` / `tool_result`** — simulated world state injected at a turn. `tool_result` with an `ERROR:` prefix is how error-recovery scenarios signal failure to the router.
- **`action`** — optional verb on a route: `route | handoff | clarify | split | escalate | stop | continue`. The evaluator uses this for stop-detection, clarification-precision, and delegation-quality metrics.
- **`success_criteria`** — free-text checks; in v0.1 these are scored via proxies (see `metrics.md`). A future version will support LLM-judge scoring against these criteria.

## The 10 task families

| Family | What it stresses | Canonical failure mode |
|---|---|---|
| `goal_clarification` | Ask when needed, don't over-ask | `premature_delegation`, `over_clarification` |
| `goal_shift` | Re-plan when the objective changes | `stale_goal_continuation` |
| `tool_routing` | Route by required capability | `wrong_specialist` |
| `multi_agent_handoff` | Correct sequencing across specialists | `wrong_order`, `premature_handoff` |
| `error_recovery` | Retry differently / escalate after failure | `blind_retry`, `infinite_loop` |
| `budget_aware` | Cheap-first unless risk triggers premium | `over_provisioning`, `under_provisioning` |
| `safety_privacy` | Detect trust-boundary crossings | `safety_violation` |
| `long_horizon_state` | Honor early constraints later | `state_loss`, `constraint_violation` |
| `parallelization` | Independent vs dependent subtasks | `over_serialization`, `over_parallelization` |
| `stop_detection` | Know when the goal is satisfied | `over_routing`, `infinite_loop` |

## Authoring guidelines

- **Multi-turn by default.** A scenario with one turn is almost always better expressed as a single-turn LLM-router benchmark. Add at least one state-evolving turn.
- **Inject failures deliberately.** Use `tool_result: "ERROR: ..."` to exercise recovery. Don't rely on stochastic model failure.
- **Prefer allowed route sets over single oracles.** If two agents could legitimately handle a turn, list both under `acceptable_alternatives`.
- **Make failure modes explicit.** Each scenario names the `routing_failures` it targets — this drives targeted metric evaluation.
- **Keep scenarios side-effect free.** The evaluator replays them synchronously. No live network calls in the loop.
- **Determinism.** Routers must produce the same decisions given the same trajectory (fix any RNG seed).

## Adding a scenario

1. Pick a family (or propose a new one via an issue).
2. Copy an existing scenario in that family as a template.
3. Write 2–4 turns with an evolving goal and/or injected state.
4. Fill in `expected_router_actions`, `acceptable_alternatives`, `success_criteria`, and `routing_failures`.
5. Validate: `python -c "from evaluator.scenario import load_scenarios; load_scenarios('benchmark/scenarios')"` (this raises on any schema violation).
6. Run the example router to sanity-check: `python evaluator/evaluate.py --router evaluator/example_router.py --out /tmp/r.json`.
