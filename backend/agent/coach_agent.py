"""The coaching agent — claude-agent-sdk wired to the coach tools.

Auth: inherits the Claude Code subscription login (see AUTH_FINDINGS.md). We
explicitly STRIP ANTHROPIC_API_KEY from this process's view so the bundled
`claude` CLI uses the subscription (Keychain OAuth) and never paid API billing.
If a long-lived token is stored in the Keychain, we export it as
CLAUDE_CODE_OAUTH_TOKEN for robustness in a packaged .app.

`stream_coach_reply` is an async generator yielding plain text chunks, consumed
by the FastAPI streaming endpoint.
"""
from __future__ import annotations

import os
from typing import AsyncIterator

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
    query,
)

from ..coach_prompt import build_system_prompt
from ..credentials import get_claude_oauth_token
from .coach_tools import ALL_TOOLS, ALLOWED_TOOL_NAMES


def _prepare_auth_env() -> None:
    """Force subscription auth for the child `claude` CLI."""
    # Never let a stray API key flip billing to pay-per-use.
    os.environ.pop("ANTHROPIC_API_KEY", None)
    # Optional: use a stored long-lived subscription token if present.
    token = None
    try:
        token = get_claude_oauth_token()
    except Exception:  # noqa: BLE001 — keyring may be unavailable in some envs
        token = None
    if token and not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = token


def _build_options(user_query: str = "") -> ClaudeAgentOptions:
    coach_server = create_sdk_mcp_server(
        name="coach",
        version="1.0.0",
        tools=ALL_TOOLS,
    )
    return ClaudeAgentOptions(
        system_prompt=build_system_prompt(user_query),
        mcp_servers={"coach": coach_server},
        allowed_tools=ALLOWED_TOOL_NAMES,
        # The coach modifies the local DB through its own tools, so we
        # auto-approve those tool calls. No filesystem/Bash built-ins needed.
        tools=[],  # remove built-in tools from context
        permission_mode="acceptEdits",
        max_turns=12,
    )


async def stream_coach_reply(prompt: str) -> AsyncIterator[str]:
    """Yield assistant text chunks for a single user message.

    Tool calls happen transparently inside the agent loop; we surface only the
    natural-language text to the chat UI.
    """
    _prepare_auth_env()
    options = _build_options(prompt)

    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock) and block.text:
                        yield block.text
            elif isinstance(message, ResultMessage):
                if message.subtype != "success":
                    yield f"\n\n[Coach-Fehler: {message.subtype}]"
    except Exception as e:  # noqa: BLE001
        yield (
            "\n\n[Auth-/Verbindungsfehler zum Coach. Bist du in Claude Code "
            f"eingeloggt? (`claude /login`). Details: {type(e).__name__}: {e}]"
        )


async def coach_reply_once(prompt: str) -> str:
    """Non-streaming convenience: collect the full reply (used in tests)."""
    chunks: list[str] = []
    async for c in stream_coach_reply(prompt):
        chunks.append(c)
    return "".join(chunks)
