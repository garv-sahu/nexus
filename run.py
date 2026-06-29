"""Command-line entry point for Nexus."""

from __future__ import annotations

import argparse
import sys

from app.agent import build_agent
from app.config import load_settings
from app.constants import APP_NAME


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description=f"{APP_NAME} desktop agent")
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Optional one-shot prompt. If omitted, Nexus starts an interactive shell.",
    )
    return parser.parse_args()


def main() -> int:
    """Run Nexus from the command line."""

    args = parse_args()
    settings = load_settings()
    agent = build_agent(settings)

    if args.prompt:
        print(agent.handle(" ".join(args.prompt)))
        return 0

    print(f"{APP_NAME} is ready. Type 'exit' or 'quit' to stop.")
    try:
        while True:
            user_input = input("You> ").strip()
            if user_input.lower() in {"exit", "quit"}:
                break
            if not user_input:
                continue
            print(f"{APP_NAME}> {agent.handle(user_input)}")
    except KeyboardInterrupt:
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
