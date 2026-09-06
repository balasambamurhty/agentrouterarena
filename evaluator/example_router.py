"""A baseline rule-based agentic router.

Not a good router — a reference implementation showing the interface and a
reasonable default policy. It demonstrates the kinds of signals an agentic
router uses (goal keywords, tool errors, prior routes, constraints).
"""
from __future__ import annotations

import re

from router_interface import RouteDecision, TurnContext


class ExampleRouter:
    """Cheap rule-based policy over (goal, state, constraints, trajectory)."""

    name = "example-rule-router"

    # Capability keywords -> agent id (see benchmark/agents.yaml).
    CAPABILITY_KEYWORDS: dict[str, list[str]] = {
        "data_agent": ["volume", "churn", "ledger", "reconcil", "row count", "sql", "dataset", "pricing page", "dashboard"],
        "coding_agent": ["pipeline", "model", "run the", "deploy", "code", "build", "feature"],
        "browser_agent": ["pricing page", "live page", "website", "check whether"],
        "calendar_agent": ["block off", "schedule", "meeting", "calendar"],
        "email_agent": ["email", "newsletter", "send", "draft", "notice", "thank-you"],
        "research_agent": ["research", "competitor", "find", "summarize", "reviews", "charter", "hike"],
        "safety_agent": ["ssn", "pii", "delete", "destructive", "refund", "legal", "contract", "ip assignment"],
        "domain_expert_agent": ["contract", "legal", "ip assignment", "medical", "finance"],
        "planning_agent": ["plan", "coordinate", "move", "trip", "outline", "status", "report", "summarize"],
        "qa_agent": ["qa", "validate", "verify", "review"],
    }

    def decide(self, ctx: TurnContext) -> RouteDecision:
        # If a tool errored on this turn, do not retry the same route.
        if ctx.current_tool_result and "ERROR" in ctx.current_tool_result.upper():
            # Pick a different agent than the immediately previous one.
            prev = ctx.history[-1].get("route_to") if ctx.history else None
            for agent, kws in self.CAPABILITY_KEYWORDS.items():
                if agent != prev and any(k in (ctx.user_goal or "").lower() for k in kws):
                    return RouteDecision(route_to=agent, action="escalate", reason="fallback after tool error")
            return RouteDecision(route_to="planning_agent", action="escalate", reason="tool error; escalate")

        text = (ctx.current_user_message or "").lower()
        # Safety / privacy: PII or destructive verbs trigger clarify/escalate.
        if any(w in text for w in ["ssn", "pii", "delete from production", "destructive"]):
            return RouteDecision(route_to="safety_agent", action="clarify", reason="sensitive/PII requires confirmation")

        # Goal clarification: very short, vague goals -> clarify.
        if ctx.turn_index == 0 and len((ctx.current_user_message or "")) < 24 and not any(
            k in text for kws in self.CAPABILITY_KEYWORDS.values() for k in kws
        ):
            return RouteDecision(route_to="planning_agent", action="clarify", reason="goal underspecified")

        # Stop detection: if the previous turn already answered, stop.
        if ctx.history and ctx.history[-1].get("assistant_state"):
            if any(w in text for w in ["what's the capital", "confirm the deploy"]):
                return RouteDecision(route_to="research_agent", action="stop", reason="goal satisfied")

        # Capability routing by keyword.
        for agent, kws in self.CAPABILITY_KEYWORDS.items():
            if any(k in text for k in kws):
                return RouteDecision(route_to=agent, reason="keyword capability match")

        # Long-horizon: if a later turn mentions adding/changing a prior plan, re-check.
        if re.search(r"\b(add|push|change|actually)\b", text) and ctx.history:
            return RouteDecision(route_to="planning_agent", reason="re-evaluate prior constraint")

        return RouteDecision(route_to="planning_agent", reason="default fallback")
