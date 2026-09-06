"""The contract every agentic router must implement.

A router is a policy over (goal, state, capabilities, constraints, trajectory).
At each decision point it returns a RouteDecision describing what to do next.

This interface intentionally mirrors how agentic routing differs from single-turn
LLM routing: the router sees the full evolving trajectory, not just one prompt.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class TurnContext:
    """Everything visible to the router at a decision point."""

    scenario_id: str
    family: str
    user_goal: str
    available_agents: list[str]
    constraints: dict[str, Any]
    # The trajectory so far: list of (user_or_state, prior_decision) pairs.
    history: list[dict[str, Any]] = field(default_factory=list)
    # The current turn's user message (may be None if this turn is a tool result).
    current_user_message: str | None = None
    # Simulated tool/agent result injected for this turn (e.g. an error).
    current_tool_result: str | None = None
    turn_index: int = 0


@dataclass
class RouteDecision:
    route_to: str
    action: str = "route"  # route | handoff | clarify | split | escalate | stop | continue
    reason: str = ""

    def matches(self, allowed: list[dict[str, Any]]) -> bool:
        """True if this decision is in the oracle/allowed route set."""
        targets = {a.get("route_to") for a in allowed}
        return self.route_to in targets


class AgenticRouter(Protocol):
    """Implement this. Routers must be deterministic given the same trajectory."""

    name: str

    def decide(self, ctx: TurnContext) -> RouteDecision: ...  # pragma: no cover
