from __future__ import annotations

import os
import shlex
import subprocess
from typing import Iterable, Tuple, Any, Dict

from .exceptions import ExecutionError


def read_text(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def read_files(paths: Iterable[str]) -> Tuple[str, str]:
    """
    Returns a tuple of (combined_prompt_context, log).
    Each file is separated with a header marker for clarity to downstream CLIs.
    """
    combined: list[str] = []
    log_parts: list[str] = []
    for p in paths:
        try:
            content = read_text(p)
            combined.append(f"\n===== FILE: {p} =====\n{content}\n")
            log_parts.append(f"Included file: {p} ({len(content)} chars)")
        except FileNotFoundError:
            log_parts.append(f"File not found: {p}")
        except Exception as e:
            log_parts.append(f"Error reading {p}: {e}")
    return ("".join(combined), "\n".join(log_parts))


def is_noninteractive() -> bool:
    return os.getenv('PYCODEX_NONINTERACTIVE', '0') == '1'


def approve_action(prompt: str) -> bool:
    if is_noninteractive():
        return False
    try:
        ans = input(f"{prompt} [y/N]: ").strip().lower()
    except EOFError:
        return False
    return ans in {"y", "yes"}


def run_subprocess(cmd: list[str], *, input_text: str | None = None, timeout: int | None = None) -> Tuple[int, str, str]:
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE if input_text is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        out, err = proc.communicate(input=input_text, timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
        return (124, out or '', err or 'Timeout expired')
    return (proc.returncode, out or '', err or '')


def exec_shell_command(command: str, *, safe: bool = True, approval_mode: str = 'suggest') -> Tuple[int, str, str]:
    """
    Execute a shell command with optional safety gating.

    approval_mode:
      - 'suggest': prompt for confirmation if safe=True
      - 'auto-edit': execute if safe=True but log that it would be executed
      - 'full-auto': execute without prompting
    """
    cmd = ['bash', '-lc', command]

    def _do_exec():
        return run_subprocess(cmd)

    if not safe or approval_mode == 'full-auto':
        return _do_exec()

    if approval_mode == 'auto-edit':
        return _do_exec()

    # 'suggest' mode
    if is_noninteractive():
        raise ExecutionError(
            "Safe execution requires approval in noninteractive mode. Set approval_mode='full-auto' or PYCODEX_NONINTERACTIVE=0."
        )
    if approve_action(f"Execute command: {command}"):
        return _do_exec()
    return (125, '', 'Command not approved by user')


def which(cmd: str) -> str | None:
    for path in os.getenv('PATH', '').split(os.pathsep):
        candidate = os.path.join(path, cmd)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def build_cli_command(base_cmd: str, subcommand: str, model: str | None, approval_mode: str | None, extra_args: list[str] | None = None) -> list[str]:
    """
    Construct a generic CLI invocation with optional flags.
    """
    parts = [base_cmd, subcommand]
    if model:
        parts += ["--model", model]
    if approval_mode:
        parts += ["--approval", approval_mode]
    if extra_args:
        parts += extra_args
    return parts


def parse_code_and_text(output: str) -> Tuple[str, str]:
    """
    Try to split CLI output into (code, text) using fenced code blocks if present.
    """
    code = ''
    text = output
    fence = '```'
    if fence in output:
        segments = output.split(fence)
        if len(segments) >= 3:
            # Assume the code is in the first fenced block
            # segments: [pre, (lang)\n code, post ...]
            code_block = segments[1]
            # Drop optional language spec on first line
            if '\n' in code_block:
                first_line, rest = code_block.split('\n', 1)
                # If first_line looks like a language tag, use rest; else keep all
                code = rest if first_line.strip() and not first_line.strip().startswith('#') else code_block
            else:
                code = code_block
            # Text becomes everything else (pre + post)
            text = (segments[0] + ''.join(segments[2:])).strip()
    return code.strip(), text.strip()


def _load_toml(path: str) -> Dict[str, Any]:
    try:
        import tomllib
        with open(path, 'rb') as f:
            return tomllib.load(f)
    except ModuleNotFoundError:
        try:
            import toml
            with open(path, 'r', encoding='utf-8') as f:
                return toml.load(f)
        except Exception:
            return {}
    except FileNotFoundError:
        return {}
    except Exception:
        return {}


def get_config() -> Dict[str, Any]:
    """
    Load config from ~/.pycodex/config.toml if present.
    Schema (optional):
      [backend.codex]
      cli = "codex"
      model = "gpt-5-codex"
      approval_mode = "suggest"
      files_arg = true
      split_edit = true
    """
    home = os.path.expanduser('~')
    path = os.path.join(home, '.pycodex', 'config.toml')
    return _load_toml(path) or {}
