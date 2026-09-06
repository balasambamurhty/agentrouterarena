# Submitting a Router

1. **Implement the interface.** Create a Python class with a `name` attribute and a `decide(ctx)` method returning a `RouteDecision`. See [`evaluator/router_interface.py`](../evaluator/router_interface.py) and the example [`evaluator/example_router.py`](../evaluator/example_router.py).

2. **Add your router.** Place it under `submissions/<your-router>/router.py` with a short `README.md`.

3. **Run the evaluator locally.**
   ```bash
   python evaluator/evaluate.py \
     --router submissions/<your-router>/router.py \
     --scenarios benchmark/scenarios \
     --out submissions/<your-router>/results.json
   ```

4. **Open a PR.** CI re-runs the evaluator and validates all scenarios against the schema. Your row appears on the leaderboard once merged.

## Rules

- **Deterministic.** Same trajectory → same decisions. Fix any RNG seed.
- **No live external calls in the loop.** The evaluator replays scenarios synchronously. If your router needs tools at inference time, that's your deployment concern — the benchmark measures routing policy, not tool execution.
- **Self-contained.** Don't read scenario files at runtime; only use what's in `TurnContext`.
- **Reproducible cost/latency.** If you claim cost/latency advantages, document the agent cost tiers you assume (see `benchmark/agents.yaml`).

## Example

See [`example_submission/`](example_submission/).
