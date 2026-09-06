"""CLI entry point: run a router against the benchmark scenarios.

Usage:
    python evaluator/evaluate.py \
        --router evaluator/example_router.py \
        --scenarios benchmark/scenarios \
        --out results.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import yaml

from router_interface import TurnContext
from scenario import load_scenarios
from scoring import aggregate, score_scenario

METRICS_PATH = Path(__file__).resolve().parent.parent / "benchmark" / "metrics.yaml"


def load_weights() -> dict[str, float]:
    data = yaml.safe_load(METRICS_PATH.read_text())
    return data["headline"]["blend"]


def load_router(path: str):
    spec = importlib.util.spec_from_file_location("router_module", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["router_module"] = module
    spec.loader.exec_module(module)
    # Expect a class named AgenticRouter OR the first Router-ish class.
    for attr in dir(module):
        obj = getattr(module, attr)
        if isinstance(obj, type) and hasattr(obj, "decide") and hasattr(obj, "name"):
            return obj()
    raise ValueError(f"No AgenticRouter subclass found in {path}")


def run_router(router, scenarios) -> list:
    results = []
    for sc in scenarios:
        ctx = TurnContext(
            scenario_id=sc["id"],
            family=sc["family"],
            user_goal=sc.get("user_goal", ""),
            available_agents=sc.get("available_agents", []),
            constraints=sc.get("constraints", {}),
        )
        decisions = []
        for i, turn in enumerate(sc.get("turns", [])):
            ctx.turn_index = i
            ctx.current_user_message = turn.get("user")
            ctx.current_tool_result = turn.get("tool_result")
            ctx.history.append({"assistant_state": turn.get("assistant_state")})
            try:
                dec = router.decide(ctx)
            except Exception as e:  # noqa: BLE001 - a router crash counts as a failed turn
                dec = type("D", (), {"route_to": "", "action": "error", "reason": str(e), "matches": lambda self, a: False})()
            decisions.append(dec)
            ctx.history[-1]["route_to"] = getattr(dec, "route_to", "")
        results.append(score_scenario(sc, decisions))
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Evaluate an agentic router against the AgentRoute Arena benchmark.")
    ap.add_argument("--router", required=True, help="Path to a .py file defining an AgenticRouter.")
    ap.add_argument("--scenarios", default="benchmark/scenarios", help="Directory of scenario YAML files.")
    ap.add_argument("--out", default="results.json", help="Where to write JSON results.")
    args = ap.parse_args(argv)

    scenarios = load_scenarios(args.scenarios)
    print(f"Loaded {len(scenarios)} scenarios")
    router = load_router(args.router)
    print(f"Loaded router: {router.name}")

    results = run_router(router, scenarios)
    weights = load_weights()
    summary = aggregate(results, weights)

    out = {
        "router": router.name,
        "n_scenarios": len(scenarios),
        "summary": summary,
        "by_scenario": [
            {
                "id": r.scenario_id,
                "family": r.family,
                "goal_completed": r.goal_completed,
                "route_accuracy": round(r.route_accuracy, 3),
                "safety_violated": r.safety_violated,
                "turns_used": r.turns_used,
                "handoffs": r.handoffs,
            }
            for r in results
        ],
    }
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(json.dumps(out["summary"], indent=2))
    print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
