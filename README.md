# AgentRoute Arena

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0) [![Scenarios: 51](https://img.shields.io/badge/scenarios-51%20across%2014%20families-06b6d4)](benchmark/scenarios/)

**An open platform for comprehensive comparison of agentic routers.**

> LLM routing picks the best model for a single prompt.
> **Agentic routing** picks the best agent, tool path, handoff, or clarification strategy across an **evolving goal state** — across many turns.

AgentRoute Arena is the agentic-routing analog of single-turn LLM-router benchmarks. Instead of a flat list of prompts, the benchmark artifact is a **multi-turn trajectory** with an evolving goal, an evolving world state, a set of available agents/tools, and a set of constraints. A router is evaluated on whether it makes the right *trajectory-level* decisions: who to route to, when to hand off, when to clarify, when to re-route, and when to stop.

---

## Why a separate benchmark for agentic routing?

Single-turn routers optimize "which model answers this prompt best." That framing breaks the moment a task becomes multi-turn:

| Dimension | LLM routing (one turn) | Agentic routing (multi-turn) |
|---|---|---|
| Unit of decision | A single prompt | A step within an evolving trajectory |
| Optimizes | Model quality / cost / latency per call | Goal completion across the whole trajectory |
| Signal available | Prompt text | Goal, state, prior turns, tool results, failures, budget |
| Decision space | Model pool | Agents, tools, handoffs, splits, clarifications, stop |
| Failure mode | Wrong model picked | Stale goal, wrong specialist, over-clarification, infinite loop |

An agentic router is a **policy engine over**:

1. **Goal** — what outcome is the user actually trying to achieve?
2. **State** — what has already happened, failed, been learned, or changed?
3. **Capabilities** — which agents/tools can act, and under what permissions?
4. **Constraints** — budget, latency, privacy, risk, completeness.
5. **Trajectory** — continue, re-route, split work, escalate, clarify, or stop.

---

## Repository layout

```text
agentroute-arena/
├── site/                       # Static site (GitHub Pages)
│   ├── index.html               # Home
│   ├── leaderboard.html         # Router rankings
│   ├── benchmark.html           # Task families + sample scenarios
│   ├── metrics.html             # Evaluation metrics
│   ├── submit.html              # How to submit a router
│   ├── about.html               # Project info
│   ├── styles.css
│   └── app.js
├── benchmark/
│   ├── schema/
│   │   └── scenario.schema.json # JSON Schema for a test case
│   ├── scenarios/               # Seed test cases (10 families)
│   │   ├── goal_clarification.yaml
│   │   ├── goal_shift.yaml
│   │   ├── tool_routing.yaml
│   │   ├── multi_agent_handoff.yaml
│   │   ├── error_recovery.yaml
│   │   ├── budget_aware.yaml
│   │   ├── safety_privacy.yaml
│   │   ├── long_horizon_state.yaml
│   │   ├── parallelization.yaml
│   │   └── stop_detection.yaml
│   ├── agents.yaml              # Reference agent/tool pool
│   └── metrics.yaml            # Metric definitions + weights
├── evaluator/
│   ├── scenario.py              # Scenario loader + validation
│   ├── router_interface.py     # The contract a router must implement
│   ├── scoring.py               # Metric computations
│   ├── evaluate.py              # CLI entry point
│   └── example_router.py       # A baseline rule-based router
├── submissions/
│   ├── README.md                # How to submit
│   └── example_submission/      # Reference submission
├── docs/
│   ├── test_case_design.md      # How scenarios are authored
│   └── metrics.md              # Metric definitions in depth
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

---

## Quick start

```bash
git clone https://github.com/<your-org>/agentroute-arena.git
cd agentroute-arena
python -m venv .venv && source .venv/bin/activate
pip install pyyaml jsonschema

# Run the baseline router against the seed scenarios
python evaluator/evaluate.py \
  --router evaluator/example_router.py \
  --scenarios benchmark/scenarios \
  --out results.json
```

A router is any Python object implementing the interface in `evaluator/router_interface.py`. See `evaluator/example_router.py` and `submissions/example_submission/`.

---

## Test cases

The benchmark ships **14 task families** with seed scenarios. Each scenario is a multi-turn trajectory with `expected_router_actions` (the oracle/allowed route set) and `success_criteria`. See `docs/test_case_design.md` and `benchmark/scenarios/`.

| Family | What it stresses |
|---|---|
| Goal clarification | Asking when needed, not over-asking |
| Goal shift | Re-planning when the objective changes mid-task |
| Tool / capability routing | Routing by required tool (browser, code, calendar, DB…) |
| Multi-agent handoff | Correct sequencing across specialists |
| Error recovery | Retry differently / downgrade / escalate after failure |
| Budget-aware routing | Cheap-first unless risk/complexity triggers premium |
| Safety / privacy boundary | Detecting trust-boundary crossings |
| Long-horizon state tracking | Honoring early constraints later |
| Parallelization vs sequencing | Independent vs dependent subtasks |
| Stop / completion detection | Knowing when the goal is satisfied |
| Context retrieval | Internal knowledge vs external search |
| Verification before action | Confirm before irreversible actions |
| Capability escalation | Escalate to a specialist when stuck |
| Multi-modal routing | Route by input modality (image/audio/chart) |

---

## Metrics

The leaderboard uses a composite **AgentRoute Score** from submetrics: goal completion rate, route decision accuracy vs. the allowed route set, re-route success, handoff efficiency, turn efficiency, recovery rate, clarification precision, cost-/latency-normalized success, safety pass rate, state retention, and delegation quality. See `docs/metrics.md`.

---

## Submitting a router

1. Fork the repo and implement `AgenticRouter` (see `evaluator/router_interface.py`).
2. Add your router under `submissions/<your-router>/`.
3. Run the evaluator locally; include `results.json`.
4. Open a PR. See `submissions/README.md`.

---

## Status

This is a v0.2 seed benchmark: 14 families, 51 seed scenarios, a reference evaluator, and a baseline router. Leaderboard rows shown on the site are **illustrative baselines** to demonstrate the format — submit a real router to appear on the live board.

## Ecosystem

AgentRoute Arena targets **multi-turn, goal-based agentic routing** — the gap
left open by most existing systems, which are **single-turn LLM routers** that
pick the best model per prompt. Notable routers in the space, with the two
open-source vendors independently tested in our sandbox:

| Router | License | Agentic fit | Status | Key capability |
| --- | --- | --- | --- | --- |
| [LiteLLM](https://github.com/BerriAI/litellm) | Open (MIT) | None | **Tested · PASS** | Load balancing, fallback-on-failure, retry-then-fallback across model deployments |
| [Kiro Gateway](https://github.com/jwadow/kiro-gateway) | Open (AGPL-3.0) | None | **Tested · 1691/1691 tests pass** | Multi-account failover proxy; OpenAI/Anthropic-compatible API over Kiro |
| [Not Diamond](https://www.notdiamond.ai/) | Closed (SaaS) | Partial | Vendor-claimed | Predicts model + reasoning effort per step using payload semantics, KV-cache state, and past-turn sequence |
| [AWS Kiro (Auto Mode)](https://kiro.dev/docs/models/available-models/) | Closed (managed) | Partial | Vendor-claimed | Built-in cost-benefit router with multi-agent task breakdown |
| [OpenRouter](https://openrouter.ai/) | Closed (SaaS) | None | Vendor-claimed | Native "Auto" mode (Not Diamond backend) over 400+ hosted models |
| [Unify](https://unify.ai/) | Closed (SaaS) | None | Vendor-claimed | Learned neural scorer + live runtime benchmarks across 100+ providers |
| [Martian](https://withmartian.com/) | Closed (SaaS) | None | Vendor-claimed | Real-time per-query model selection ("first LLM router") |
| [RouterArena](https://routeworks.github.io/) | Open benchmark | n/a | Reference | The single-turn LLM-router benchmark this project extends |

This is a **capability survey, not the AgentRoute Score benchmark** — these are
LLM gateway / model routers, not multi-turn agentic routers, so they can't be
scored on the 51 trajectory scenarios. Full methodology and reproducible test
scripts: [`docs/vendor-testing.md`](docs/vendor-testing.md) and
[`benchmark/vendors/test_litellm_router.py`](benchmark/vendors/test_litellm_router.py).

Single-turn routers answer "which model for this prompt?" AgentRoute Arena
answers "which agent, tool path, handoff, or clarification across this evolving
goal?" — the multi-turn complement to the systems above. Not Diamond and AWS
Kiro are the closest existing systems to agentic routing (session / multi-agent
aware); the rest are single-turn selectors or failover proxies.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
