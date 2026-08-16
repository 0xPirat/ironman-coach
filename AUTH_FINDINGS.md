# AUTH FINDINGS — How the coach authenticates

**Verdict: SUBSCRIPTION AUTH WORKS HEADLESSLY. ✅**

The `claude-agent-sdk` (Python) ran a real query end-to-end using **only the
Claude Code subscription login** (OAuth) already on this machine, with **no
`ANTHROPIC_API_KEY` set**. We chose this as the primary approach. No fallback was
needed.

## What was actually tested

- Machine state at test time:
  - `claude` CLI version: **2.1.158** (`/Users/johannesbenedict/.local/bin/claude`)
  - `ANTHROPIC_API_KEY`: **NOT set**
  - macOS Keychain contains a generic-password item named **`Claude Code-credentials`**
    (this is the Claude Code OAuth login, created by `claude /login`).
  - `claude-agent-sdk` version: **0.2.87**, Python 3.14.
- Spike: [`spikes/auth_spike.py`](spikes/auth_spike.py). It refuses to run if
  `ANTHROPIC_API_KEY` is present (so the test is honest), then issues one
  `query(...)` with all built-in tools removed.
- Result: `subtype=success`, the model replied `AUTH_OK 2026`, reported cost
  `~$0.00138`. **Exit code 0.**

## Why this works

The Python `claude-agent-sdk` does **not** talk to the Anthropic REST API
directly. It spawns the bundled/installed **`claude` CLI** as a subprocess and
speaks a control protocol to it. The CLI resolves credentials in this order:

1. `ANTHROPIC_API_KEY` env var (pay-per-use API billing) — **we deliberately
   leave this UNSET**.
2. `CLAUDE_CODE_OAUTH_TOKEN` env var (a long-lived subscription token from
   `claude setup-token`).
3. The interactive login stored in the macOS Keychain as
   `Claude Code-credentials` (from `claude /login`) — **this is what we use**.

Because the SDK inherits the CLI's auth, the user's Claude Max/Pro subscription
is used for billing, exactly as required. No API tokens are spent.

## What the USER must do — ONCE

1. Install the Claude Code CLI (already present here: v2.1.158).
2. Log in with the subscription account:
   ```
   claude /login
   ```
   Complete the browser OAuth flow. This writes `Claude Code-credentials` to the
   macOS Keychain. That is the whole setup.
3. **Do NOT export `ANTHROPIC_API_KEY`** in the shell/launch environment that
   runs the Python sidecar, or the CLI will switch to paid API billing. The
   sidecar explicitly strips `ANTHROPIC_API_KEY` from the subprocess env as a
   guard (see `backend/agent/coach_agent.py`).

### Optional, more robust for a packaged app

For a `.app` launched from Finder (which has a minimal environment and may not
see the Keychain login reliably in all macOS versions), generate a long-lived
token once:

```
claude setup-token
```

Store the printed token in the Keychain (the backend exposes
`backend/credentials.py` helpers, service `ironman-coach`, key
`claude_oauth_token`) and the sidecar will export it as `CLAUDE_CODE_OAUTH_TOKEN`
for the CLI. This is the recommended path for the shipped app; the interactive
Keychain login is fine for dev.

## Caveats / honesty

- Subscription OAuth is intended for **individual, interactive** use. Anthropic
  has signalled that heavy multi-tenant automation should use API keys. This app
  is single-user, local, and interactive — squarely the intended use — but if
  Anthropic tightens enforcement, the fallback is `CLAUDE_CODE_OAUTH_TOKEN` or,
  last resort, an API key (one-line change in `coach_agent.py`).
- The token/login can expire; the user re-runs `claude /login` or
  `claude setup-token` if the coach starts returning auth errors. The sidecar
  surfaces auth failures clearly to the chat UI.

## Approach chosen

**Primary:** `claude-agent-sdk` `query()` / `ClaudeSDKClient`, inheriting the
Claude Code Keychain OAuth login, `ANTHROPIC_API_KEY` stripped from the child
env. **Confirmed working.** No subprocess `claude -p` fallback required.
