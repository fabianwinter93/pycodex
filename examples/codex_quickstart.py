#!/usr/bin/env python3
"""
Minimal Codex backend example using the pycodex facade.

Usage:
  python examples/codex_quickstart.py

Environment (optional):
  PYCODEX_CODEX_CLI     Path to `codex` binary (default: "codex")
  PYCODEX_CODEX_MODEL   Model name (default: "gpt-5-codex")
  PYCODEX_CODEX_SANDBOX Sandbox mode: read-only | workspace-write | danger-full-access
"""
from __future__ import annotations

import os
from pycodex import PyCodex
from pycodex import BackendNotFoundError, ExecutionError


def main() -> None:
    # Initialize facade for Codex backend. Model can be overridden via env.
    model = os.getenv("PYCODEX_CODEX_MODEL", "gpt-5-codex")
    coder = PyCodex(backend="codex", model=model, approval_mode="suggest")

    print(f"-> Using Codex model: {model}")

    # 1) Generate code
    print("\n[1/4] Generating a function...")
    gen = coder.generate(
        "Write a Python function named reverse_string(s) that returns the reversed string. "
        "Respond with only the function in a fenced code block.")
    print(gen.code or gen.text)

    # 2) Explain code
    to_explain = gen.code or """def reverse_string(s):\n    return s[::-1]\n"""
    print("\n[2/4] Explaining the code...")
    exp = coder.explain(to_explain)
    print(exp.text or exp.code)

    # 3) Edit code according to instructions
    print("\n[3/4] Editing a buggy function...")
    buggy = "def add(a, b):\n    return a\n"
    edit = coder.edit(buggy, "Fix the function to return a + b and add a short docstring.")
    print(edit.code or edit.text)

    # 4) Run a benign shell command (non-destructive). Set safe=False to avoid prompts.
    print("\n[4/4] Running a shell command (echo)...")
    cmd = coder.exec_command("echo 'Codex quickstart complete.'", safe=False)
    print(cmd.output or cmd.error)


if __name__ == "__main__":
    try:
        main()
    except BackendNotFoundError as e:
        print(f"Codex CLI not found: {e}")
        print("Hint: install Codex CLI and/or set PYCODEX_CODEX_CLI to its path.")
    except ExecutionError as e:
        print(f"Execution failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

