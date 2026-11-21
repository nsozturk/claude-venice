# AGENTS.md — `claude-venice` Agent Contract

This file defines how AI coding agents (Claude Code, Codex, Antigravity, Gemini CLI, Cursor, OpenCode) should invoke, test, and maintain `claude-venice`.

## What `claude-venice` Does

`claude-venice` is a zero-dependency Bash launcher that starts the `claude` CLI against a local `venice-adapters` (`127.0.0.1:18892`) -> `venice-bridge` (`127.0.0.1:18891`) stack inside an isolated `~/.claude-venice` profile.

## Non-Interactive Invocation

Always close stdin (`</dev/null`) and pass `-p "<prompt>"` when running from another agent or script:

```bash
claude-venice --lean -p "Summarize git status in one line." </dev/null
```

## Operational Truths

- **Default model:** `deepseek-v4-1-flash-uncensored` (override with `-m <id>` or `VENICE_CLAUDE_MODEL`).
- **Default permissions:** Adds `--dangerously-skip-permissions --permission-mode bypassPermissions` unless `VENICE_CLAUDE_SKIP_PERMS=0` or another `--permission-mode` is passed. Explicitly passing `--permission-mode bypassPermissions` also pairs `--dangerously-skip-permissions`.
- **`--lean` flag:** Injects `--strict-mcp-config --mcp-config '{"mcpServers":{}}'` (or preserves caller's `--mcp-config` if already supplied). Prefer `--lean` for automated runs to keep `[TOOLS]` compact.
- **Preflight checks:** Exits `1` immediately with an actionable message if `venice-bridge` (`:18891/health`), `venice-adapters` (`:18892/health`), or the Venice session is inactive.
- **Inspection commands (exit 0, no LLM call):**
  - `claude-venice --models`
  - `claude-venice --quota`

## Verification

Run the offline unit test suite (stubs `curl` and `claude`, zero network calls):

```bash
python3 test_claude_venice.py
```

## Security & Privacy

- Never commit `~/.claude-venice/`, session transcripts, cookies, or JWTs.
- Never print live `venice.ai` cookies or Clerk tokens.
