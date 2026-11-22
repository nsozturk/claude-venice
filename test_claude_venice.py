#!/usr/bin/env python3
"""Unit tests for claude-venice launcher flag parsing (incl. --lean)."""
import json
import os
import stat
import subprocess
import tempfile

LAUNCHER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "claude-venice")


def make_fake_bin(tmpdir: str) -> str:
    bindir = os.path.join(tmpdir, "bin")
    os.makedirs(bindir, exist_ok=True)
    # Stub curl: returns healthy bridge + adapter JSON
    curl_p = os.path.join(bindir, "curl")
    with open(curl_p, "w") as f:
        f.write('#!/usr/bin/env bash\necho \'{"ok": true, "venice_session": "active", "chat_quota": {"remaining": 5000}}\'\n')
    os.chmod(curl_p, 0o755)
    # Stub claude: dumps env MODEL + BASE_URL + AUTH_SET + argv as JSON
    claude_p = os.path.join(bindir, "claude")
    with open(claude_p, "w") as f:
        f.write(
            '#!/usr/bin/env python3\n'
            'import json, os, sys\n'
            'print(json.dumps({"model": os.environ.get("ANTHROPIC_MODEL"), '
            '"base_url": os.environ.get("ANTHROPIC_BASE_URL"), '
            '"has_token": bool(os.environ.get("ANTHROPIC_AUTH_TOKEN")), '
            '"argv": sys.argv[1:]}))\n'
        )
    os.chmod(claude_p, 0o755)
    return bindir


def run_launcher(bindir: str, args: list, extra_env: dict = None) -> dict:
    env = os.environ.copy()
    env["PATH"] = bindir + ":" + env.get("PATH", "")
    if extra_env:
        env.update(extra_env)
    out = subprocess.check_output(["bash", LAUNCHER] + args, env=env, text=True)
    return json.loads(out.strip().splitlines()[-1])


def main():
    with tempfile.TemporaryDirectory(prefix="claude-venice-test-") as tmp:
        bindir = make_fake_bin(tmp)

        # 1. Default: no --lean -> no --strict-mcp-config, has --dangerously-skip-permissions
        r = run_launcher(bindir, ["-p", "hi"])
        assert "--strict-mcp-config" not in r["argv"], r
        assert "--mcp-config" not in r["argv"], r
        assert "--dangerously-skip-permissions" in r["argv"], r
        assert r["model"] == "deepseek-v4-1-flash-uncensored", r

        # 2. --lean before -p
        r = run_launcher(bindir, ["--lean", "-p", "hi"])
        assert "--lean" not in r["argv"], r
        assert "--strict-mcp-config" in r["argv"], r
        idx = r["argv"].index("--mcp-config")
        assert r["argv"][idx + 1] == '{"mcpServers":{}}', r
        assert r["argv"][-2:] == ["-p", "hi"], r

        # 3. -m <model> --lean
        r = run_launcher(bindir, ["-m", "z-ai-glm-5-3-flash", "--lean", "-p", "hi"])
        assert r["model"] == "z-ai-glm-5-3-flash", r
        assert "--lean" not in r["argv"], r
        assert "--strict-mcp-config" in r["argv"], r

        # 4. --lean -m <model>
        r = run_launcher(bindir, ["--lean", "-m", "qwen-3-8-27b", "-p", "hi"])
        assert r["model"] == "qwen-3-8-27b", r
        assert "--lean" not in r["argv"], r
        assert "--strict-mcp-config" in r["argv"], r

        # 5. --lean after other flags (e.g. -p hi --lean)
        r = run_launcher(bindir, ["-p", "hi", "--lean"])
        assert "--lean" not in r["argv"], r
        assert "--strict-mcp-config" in r["argv"], r

        # 6. Respect caller's own --mcp-config even with --lean
        r = run_launcher(bindir, ["--lean", "--mcp-config", "/tmp/custom.json", "-p", "hi"])
        assert r["argv"].count("--mcp-config") == 1, r
        assert "/tmp/custom.json" in r["argv"], r
        assert "--strict-mcp-config" in r["argv"], r

        # 7. Zero args and bare --lean do not trip bash set -u on empty PASS_ARGS
        r = run_launcher(bindir, [])
        assert r["argv"] == ["--dangerously-skip-permissions", "--permission-mode", "bypassPermissions"], r
        r = run_launcher(bindir, ["--lean"])
        assert "--strict-mcp-config" in r["argv"] and "--lean" not in r["argv"], r
        # 8. Explicit --permission-mode bypassPermissions still gets --dangerously-skip-permissions; other modes do not
        r = run_launcher(bindir, ["--permission-mode", "bypassPermissions", "-p", "hi"])
        assert "--dangerously-skip-permissions" in r["argv"], r
        r = run_launcher(bindir, ["--permission-mode", "plan", "-p", "hi"])
        assert "--dangerously-skip-permissions" not in r["argv"], r

        # 9. --unquant uses Unquant default model & strips --unquant from argv
        r = run_launcher(
            bindir,
            ["--unquant", "-p", "hi"],
            extra_env={"UNQUANT_API_KEY": "test-dummy-key", "UNQUANT_BASE_URL": "https://api.unquant.io"},
        )
        assert "--unquant" not in r["argv"], r
        assert r["model"] == "deepseek-v4.1-flash-1017", r
        assert r["base_url"] == "https://api.unquant.io", r
        assert r["has_token"] is True, r

        # 10. --unquant with explicit -m and --lean
        r = run_launcher(
            bindir,
            ["--unquant", "-m", "glm-5.3-flash", "--lean", "-p", "hi"],
            extra_env={"UNQUANT_API_KEY": "test-dummy-key", "UNQUANT_BASE_URL": "https://api.unquant.io"},
        )
        assert "--unquant" not in r["argv"] and "--lean" not in r["argv"], r
        assert r["model"] == "glm-5.3-flash", r
        assert "--strict-mcp-config" in r["argv"], r

        # 11. --zai uses Z.AI Coding Plan default glm-5.3 & Anthropic endpoint
        r = run_launcher(
            bindir,
            ["--zai", "-p", "hi"],
            extra_env={"ZAI_API_KEY": "test-dummy-zai-key"},
        )
        assert "--zai" not in r["argv"], r
        assert r["model"] == "glm-5.3", r
        assert r["base_url"] == "https://api.z.ai/api/anthropic", r
        assert r["has_token"] is True, r

        # 12. --zai with explicit -m and --lean
        r = run_launcher(
            bindir,
            ["--zai", "-m", "glm-5.3-flash", "--lean", "-p", "hi"],
            extra_env={"ZAI_API_KEY": "test-dummy-zai-key"},
        )
        assert "--zai" not in r["argv"] and "--lean" not in r["argv"], r
        assert r["model"] == "glm-5.3-flash", r
        assert "--strict-mcp-config" in r["argv"], r

        # 13. --go / --opencode-go uses OpenCode Go default mimo-v2.6-flash & Anthropic endpoint
        r = run_launcher(
            bindir,
            ["--go", "-p", "hi"],
            extra_env={"OPENCODE_GO_API_KEY": "test-dummy-go-key"},
        )
        assert "--go" not in r["argv"], r
        assert r["model"] == "mimo-v2.6-flash", r
        assert r["base_url"] == "https://opencode.ai/inference/go/anthropic", r
        assert r["has_token"] is True, r

        # 14. --opencode-go with explicit -m and --lean
        r = run_launcher(
            bindir,
            ["--opencode-go", "-m", "qwen4-max", "--lean", "-p", "hi"],
            extra_env={"OPENCODE_GO_API_KEY": "test-dummy-go-key"},
        )
        assert "--opencode-go" not in r["argv"] and "--lean" not in r["argv"], r
        assert r["model"] == "qwen4-max", r
        assert "--strict-mcp-config" in r["argv"], r

    print("claude-venice --lean + --unquant + --zai + --go tests ok")


if __name__ == "__main__":
    main()
