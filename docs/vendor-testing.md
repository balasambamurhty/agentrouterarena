# Vendor routing-capability testing

This documents how the open-source routers in the ecosystem were **independently
tested** in our sandbox, and how closed-source vendors were assessed. This is a
**capability survey, not the AgentRoute Score benchmark** — the vendors here are
LLM gateway / model routers (failover, load-balancing, per-prompt model
selection), not multi-turn agentic routers, so they cannot be scored on the 51
trajectory scenarios in `benchmark/scenarios/`.

## Scope

| Router | License | Routing scope | Agentic fit | Independently tested |
| --- | --- | --- | --- | --- |
| [LiteLLM](https://github.com/BerriAI/litellm) | MIT | Gateway proxy + model router | None | **Yes** |
| [Kiro Gateway](https://github.com/jwadow/kiro-gateway) | AGPL-3.0 | Gateway proxy (account failover) | None | **Yes** |
| [Not Diamond](https://www.notdiamond.ai/) | Closed (SaaS) | Coding-agent router | Partial | No (vendor-claimed) |
| [AWS Kiro (Auto Mode)](https://kiro.dev/docs/models/available-models/) | Closed (managed) | Coding-agent router | Partial | No (vendor-claimed) |
| [OpenRouter](https://openrouter.ai/) | Closed (SaaS) | Model router (400+ models) | None | No (vendor-claimed) |
| [Unify](https://unify.ai/) | Closed (SaaS) | Model router (100+ providers) | None | No (vendor-claimed) |
| [Martian](https://withmartian.com/) | Closed (SaaS) | Model router | None | No (vendor-claimed) |

"Agentic fit" = whether the system makes multi-turn, goal-based routing
decisions. Not Diamond and AWS Kiro are the closest (session/multi-agent aware);
the rest are single-turn model selectors or failover proxies.

## LiteLLM Router (MIT) — independently tested

Reproducible test: [`benchmark/vendors/test_litellm_router.py`](../benchmark/vendors/test_litellm_router.py)

```bash
pip install litellm
python benchmark/vendors/test_litellm_router.py
```

Uses `litellm.Router` with `mock_response` so **no real API keys are required**.

| Capability | Result | Evidence |
| --- | --- | --- |
| Load balancing (`simple-shuffle`) | PASS | 30 requests distributed across 3 deployments (16 / 8 / 6) |
| Fallback on failure | PASS | Dead primary deployment → fell back to backup, returned backup's response |
| Retry-then-fallback | PASS | With `num_retries=2`, retried primary then fell back to backup |
| Latency-based routing | Not exercised | Runs, but selection is meaningless with mocks (all deployments ~0 latency) |
| Cost-based routing | Not exercised | Requires real usage/cost data to be meaningful |

**Agentic fit: none.** LiteLLM routes between model *deployments*, not across an
evolving multi-turn goal — it is a gateway/model router, not an agentic router.

## Kiro Gateway (AGPL-3.0) — independently tested

Kiro Gateway is a FastAPI proxy exposing an OpenAI/Anthropic-compatible API over
the Kiro API (Amazon Q Developer / CodeWhisperer), with multi-account failover.

Reproducible test — run the project's own test suite:

```bash
git clone https://github.com/jwadow/kiro-gateway
cd kiro-gateway
pip install -r requirements.txt
python -m pytest -q
```

**Result: 1691 passed, 0 failures (7.5s).** The suite covers OpenAI/Anthropic
streaming, Kiro stream parsing, error/timeout handling, multi-account failover
logic, and config validation (4 minor warnings, unrelated to failures).

**Agentic fit: none.** Kiro Gateway is an account-failover proxy, not a model
router — it does not select between models based on a query.

## Closed-source vendors

Not Diamond, AWS Kiro, OpenRouter, Unify, and Martian are closed-source SaaS /
managed services and **could not be independently tested**. Their capabilities
are taken from vendor documentation and marked "vendor-claimed" on the
leaderboard. Notably, Not Diamond documents that it considers payload semantics,
KV-cache state, and the sequence of past turns for coding-agent sessions — the
closest existing system to agentic routing.

## How this differs from the AgentRoute Score leaderboard

The AgentRoute Score leaderboard evaluates **agentic routers** that emit
`route_to` / `action` decisions over the 51 multi-turn trajectory scenarios. The
vendors here are gateway/model routers that do not make goal-based routing
decisions, so they appear on this separate **Ecosystem Leaderboard** with a
capability survey rather than an AgentRoute Score.
