"""Scenario loader and validation against the JSON schema."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

import yaml
from jsonschema import Draft7Validator

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "benchmark" / "schema" / "scenario.schema.json"

_scenario_schema: dict[str, Any] | None = None


def scenario_schema() -> dict[str, Any]:
    global _scenario_schema
    if _scenario_schema is None:
        _scenario_schema = json.loads(SCHEMA_PATH.read_text())
    return _scenario_schema


def validate_scenario(scenario: dict[str, Any]) -> list[str]:
    """Return a list of validation errors (empty if valid)."""
    errors: list[str] = []
    validator = Draft7Validator(scenario_schema())
    for err in validator.iter_errors(scenario):
        loc = ".".join(str(p) for p in err.path) or "<root>"
        errors.append(f"{loc}: {err.message}")
    # Semantic checks beyond the schema.
    if "turns" in scenario and scenario["turns"]:
        if "user" not in scenario["turns"][0] and "assistant_state" not in scenario["turns"][0]:
            errors.append("turns[0]: first turn should carry a user message")
    # Every route target must be in available_agents (consistency check).
    pool = set(scenario.get("available_agents", []))
    for i, turn in enumerate(scenario.get("turns", [])):
        for key in ("expected_router_actions", "acceptable_alternatives"):
            for j, action in enumerate(turn.get(key, [])):
                target = action.get("route_to")
                if target and target not in pool:
                    errors.append(f"turns.{i}.{key}.{j}: route_to '{target}' not in available_agents")
    return errors


def load_scenario_file(path: Path) -> list[dict[str, Any]]:
    """A scenario file may contain a YAML list of scenarios."""
    data = yaml.safe_load(path.read_text())
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a YAML list of scenarios")
    return data


def load_scenarios(directory: str | Path) -> list[dict[str, Any]]:
    """Load and validate all scenarios from a directory tree."""
    root = Path(directory)
    scenarios: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.yaml")):
        for sc in load_scenario_file(path):
            errs = validate_scenario(sc)
            if errs:
                joined = "; ".join(errs)
                raise ValueError(f"{path}: scenario {sc.get('id', '?')} invalid: {joined}")
            scenarios.append(sc)
    return scenarios


def iter_turns(scenario: dict[str, Any]) -> Iterator[dict[str, Any]]:
    for turn in scenario.get("turns", []):
        yield turn
