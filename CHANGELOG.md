# Changelog

All notable changes to `claude-venice` are documented in this file.
Versions follow [Semantic Versioning](https://semver.org/).

## 1.0.1 — 2026-11-21

### Changed

- Documented the optional `cv` terminal shortcut (`~/.local/bin/cv -> claude-venice`) for launching Claude Code in `bypassPermissions` mode.
- Documented `venice-bridge >= 0.2.5` as the recommended backend for Claude Code `2.1.329` tool-schema parity, explicit `webEnabled: false` default, and read-only SQLite / date / deferred grep & glob routing.

## 1.0.0 — 2026-11-21

### Added

- Standalone `claude-venice` Bash launcher for running Claude Code against a local [`venice-bridge`](https://github.com/nsozturk/venice-bridge) + `venice-adapters` instance in an isolated `~/.claude-venice` profile.
- `--lean` mode (`--strict-mcp-config --mcp-config '{"mcpServers":{}}'`) to disable MCP servers and keep the `[TOOLS]` prompt block compact on repos with `.mcp.json`.
- `-m <model-id>` and `VENICE_CLAUDE_MODEL` overrides (default: `deepseek-v4-1-flash-uncensored`; supports `:web`, `:xsearch`, `:think`, `venice-auto`, and local `ollama/<model>` pass-through).
- `--models` and `--quota` inspection commands plus automatic preflight health checks and low-quota warnings (`< 500` requests remaining).
- Default `--dangerously-skip-permissions --permission-mode bypassPermissions` pairing so both fresh and `--resume <session-id>` sessions run without interactive permission prompt loops (opt out via `VENICE_CLAUDE_SKIP_PERMS=0` or an explicit `--permission-mode`).
- Unit test suite (`test_claude_venice.py`) verifying flag ordering, `--lean`, `--mcp-config`, empty-arg `set -u` safety, and permission-mode forwarding.
