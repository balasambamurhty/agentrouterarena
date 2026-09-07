# Example Submission: rule-router

A trivial rule-based agentic router. This is the same policy as
[`evaluator/example_router.py`](../../evaluator/example_router.py), packaged as a
submission to show the expected layout.

```bash
python evaluator/evaluate.py \
  --router submissions/example_submission/router.py \
  --scenarios benchmark/scenarios \
  --out submissions/example_submission/results.json
```

Expected: **AgentRoute Score ≈ 44** (v0.2, 51 scenarios). This is a baseline to
beat — a real submission should improve goal completion, clarification precision,
and recovery rate.
