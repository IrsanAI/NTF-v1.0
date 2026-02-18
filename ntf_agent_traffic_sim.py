#!/usr/bin/env python3
"""Scenario simulator for long-context agent-to-agent traffic using NTF scoring."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Dict, List

from ntf_standard import run_ntf


@dataclass
class Scenario:
    name: str
    agents: int
    avg_messages_per_agent_day: int
    avg_tokens_per_message: int
    criticality: str
    payload_template: str


SCENARIOS: Dict[str, Scenario] = {
    "finance": Scenario(
        name="Finance Treasury Agents",
        agents=320,
        avg_messages_per_agent_day=180,
        avg_tokens_per_message=840,
        criticality="high",
        payload_template=(
            "anchor state relay consensus checkpoint deploy drift pulse mirror "
            "context baseline handoff align merge future compress"
        ),
    ),
    "trading": Scenario(
        name="Autonomous Trading Swarm",
        agents=1200,
        avg_messages_per_agent_day=420,
        avg_tokens_per_message=560,
        criticality="high",
        payload_template=(
            "overclock pulse drift relay anchor state consensus deploy horizon "
            "align handoff update accelerate compress route"
        ),
    ),
    "medical": Scenario(
        name="Clinical Decision Agents",
        agents=540,
        avg_messages_per_agent_day=95,
        avg_tokens_per_message=1250,
        criticality="critical",
        payload_template=(
            "anchor checkpoint state mirror synthesis consensus relay context "
            "align baseline future compress fold merge"
        ),
    ),
    "history": Scenario(
        name="Civilization History Graph Agents",
        agents=280,
        avg_messages_per_agent_day=70,
        avg_tokens_per_message=1900,
        criticality="medium",
        payload_template=(
            "horizon mirror weave synthesis state anchor relay consensus "
            "future context align fold compress merge"
        ),
    ),
    "bci": Scenario(
        name="Neural-Link BCI Mediation Agents",
        agents=2200,
        avg_messages_per_agent_day=680,
        avg_tokens_per_message=310,
        criticality="critical",
        payload_template=(
            "pulse state relay anchor checkpoint resonance drift mirror "
            "align context future fold compress overclock"
        ),
    ),
}


def build_payload(template: str, approx_tokens: int) -> str:
    words = template.split()
    filler = "latency budget policy trace packet evidence".split()
    payload = []

    while len(payload) < approx_tokens:
        payload.extend(words)
        payload.extend(filler)

    return " ".join(payload[:approx_tokens])


def simulate(scenario: Scenario) -> Dict[str, object]:
    daily_tokens_raw = (
        scenario.agents
        * scenario.avg_messages_per_agent_day
        * scenario.avg_tokens_per_message
    )

    sample_payload = build_payload(
        scenario.payload_template,
        approx_tokens=min(4500, scenario.avg_tokens_per_message * 3),
    )
    compression = run_ntf(sample_payload)
    compression_x = (
        round(compression.original_words / compression.compressed_tokens, 2)
        if compression.compressed_tokens
        else 0.0
    )

    projected_daily_tokens_ntf = int(daily_tokens_raw / compression_x) if compression_x else daily_tokens_raw
    saved_tokens_day = daily_tokens_raw - projected_daily_tokens_ntf

    return {
        "scenario": asdict(scenario),
        "daily_tokens_raw": daily_tokens_raw,
        "sample_intfr": compression.intfr,
        "sample_compression_x": compression_x,
        "projected_daily_tokens_ntf": projected_daily_tokens_ntf,
        "estimated_daily_tokens_saved": saved_tokens_day,
        "used_vocab": compression.used_vocab,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate A2A traffic scenarios for NTF")
    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=list(SCENARIOS.keys()),
        choices=list(SCENARIOS.keys()),
        help="Subset of scenario keys to simulate",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    results: List[Dict[str, object]] = [simulate(SCENARIOS[key]) for key in args.scenarios]

    if args.json:
        print(json.dumps(results, indent=2))
        return

    for item in results:
        scenario = item["scenario"]
        print(f"\n=== {scenario['name']} ({scenario['criticality']}) ===")
        print(f"Agents: {scenario['agents']}")
        print(f"Daily raw tokens: {item['daily_tokens_raw']:,}")
        print(f"Sample compression: {item['sample_compression_x']}x")
        print(f"Sample INTFR: {item['sample_intfr']}")
        print(f"Projected daily tokens via NTF: {item['projected_daily_tokens_ntf']:,}")
        print(f"Estimated tokens saved/day: {item['estimated_daily_tokens_saved']:,}")
        print(f"Used NTF vocab: {', '.join(item['used_vocab'])}")


if __name__ == "__main__":
    main()
