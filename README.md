PyCodex: Python wrapper for Codex CLI

Overview
- Provides a small, Pythonic facade over the Codex CLI for automation: generate, explain, edit, and safe command execution.
- Decouples your Python scripts from the specific Codex CLI flags; swap models/config without changing your code.

Status
- Codex backend implemented. Gemini backend is a placeholder and intentionally not wired for now.

Install
- Requires Python 3.11+ (tested with 3.13).
- Requires Codex CLI installed and available on PATH (binary name `codex`).
  - Or set `PYCODEX_CODEX_CLI` to the full path of your Codex binary.

Usage
```python
from pycodex import PyCodex

coder = PyCodex(backend='codex', model='gpt-5-codex')

# Generate
res = coder.generate('Write a Python function to reverse a string')
print(res.code or res.text)

# Explain
res = coder.explain('def add(a,b): return a+b')
print(res.text)

# Edit
res = coder.edit('def add(a,b):\n    return a', 'Fix to return a + b')
print(res.code or res.text)

# Execute shell command
cmd = coder.exec_command('echo Hello', safe=False)
print(cmd.output)
```

Example Script
- See `examples/codex_quickstart.py` for a runnable end-to-end example.

Configuration
- Env vars:
  - `PYCODEX_CODEX_CLI` path to `codex` binary
  - `PYCODEX_CODEX_MODEL` model name (e.g., `gpt-5-codex`)
  - `PYCODEX_CODEX_SANDBOX` sandbox mode: `read-only`, `workspace-write`, `danger-full-access`
- Optional `~/.pycodex/config.toml` (read by the wrapper) supports:
  ```toml
  [backend.codex]
  cli = "codex"
  model = "gpt-5-codex"
  sandbox = "workspace-write"
  ```

Notes
- The original Codex sources are NOT included here; this project only shells out to the installed CLI.
- `codex exec` runs headless and uses `--output-last-message` to capture the final message for parsing.

