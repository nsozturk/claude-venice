# Global Agent Rule — `claude-venice`

Copy this snippet into `~/.claude/agents/claude-venice.md` or your agent's global instructions:

```markdown
## claude-venice (Claude Code on Venice Web, $0 API cost)

Use `claude-venice` to run Claude Code against a local `venice-bridge` + `venice-adapters` stack in an isolated `~/.claude-venice` profile without touching the official `claude` login.

- Always close stdin (`</dev/null`) and prefer `--lean` for non-interactive runs:
  `claude-venice --lean -p "<task>" </dev/null`
- Check quota or models without spending a turn:
  `claude-venice --quota` · `claude-venice --models`
- Override model: `claude-venice -m <venice-model-id> ...` (supports `:web`, `:xsearch`, `:think`, `venice-auto`, `ollama/<id>`).
- Default mode is `bypassPermissions` (works on `--resume` too); set `VENICE_CLAUDE_SKIP_PERMS=0` to restore prompts.
```
