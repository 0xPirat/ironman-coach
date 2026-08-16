#!/usr/bin/env python3
"""
AUTH SPIKE — riskiest assumption first.

Goal: prove the claude-agent-sdk can run ONE query using ONLY the Claude Code
subscription login (OAuth credentials already on the machine), with NO
ANTHROPIC_API_KEY set.

The claude-agent-sdk spawns the `claude` CLI under the hood. The CLI, when the
user is logged in via `claude /login` (Claude Pro/Max subscription), stores an
OAuth credential in the macOS Keychain ("Claude Code-credentials"). The SDK
inherits that login automatically — no API key needed.

Run:
    cd /Users/johannesbenedict/ironman-coach
    .venv/bin/python spikes/auth_spike.py
"""

import asyncio
import os
import sys


async def main() -> int:
    # Make the test honest: refuse to run if an API key is present, because then
    # we would not actually be proving subscription auth.
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is set — unset it to test subscription auth honestly.")
        return 2

    try:
        from claude_agent_sdk import (
            query,
            ClaudeAgentOptions,
            AssistantMessage,
            TextBlock,
            ResultMessage,
        )
    except ImportError as e:
        print(f"claude-agent-sdk not installed: {e}")
        return 3

    options = ClaudeAgentOptions(
        # Keep the agent minimal: no built-in tools, no filesystem access.
        system_prompt="You are a terse test harness. Answer in one short sentence.",
        tools=[],  # remove all built-in tools from context
        max_turns=1,
    )

    print("Sending one query via subscription auth (no API key)...\n")
    answer_text = ""
    result_subtype = None
    cost = None

    try:
        async for message in query(
            prompt="Reply with exactly: AUTH_OK and the current year.",
            options=options,
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        answer_text += block.text
            elif isinstance(message, ResultMessage):
                result_subtype = message.subtype
                cost = getattr(message, "total_cost_usd", None)
    except Exception as e:
        print("QUERY FAILED.")
        print(f"  error type: {type(e).__name__}")
        print(f"  error: {e}")
        print("\nVERDICT: subscription auth did NOT work headlessly via the SDK.")
        print("See AUTH_FINDINGS.md for the fallback (subprocess `claude -p`).")
        return 1

    print(f"Assistant said: {answer_text.strip()!r}")
    print(f"Result subtype: {result_subtype}")
    print(f"Reported cost (usd): {cost}")
    print()

    if result_subtype == "success" and answer_text.strip():
        print("VERDICT: SUBSCRIPTION AUTH WORKS headlessly via claude-agent-sdk.")
        print("The SDK inherited the Claude Code OAuth login. No API key was used.")
        return 0

    print("VERDICT: ambiguous — query returned but without a clean success result.")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
