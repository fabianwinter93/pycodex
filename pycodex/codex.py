from __future__ import annotations

import os
from typing import Optional, List

from .cli_wrapper import CodexInterface, CodexResult, CommandResult
from .exceptions import BackendNotFoundError, ExecutionError
from .utils import (
    exec_shell_command,
    parse_code_and_text,
    read_files,
    run_subprocess,
    which,
    get_config,
)


class CodexBackend(CodexInterface):
    def __init__(self, model: Optional[str] = 'gpt-5-codex', approval_mode: str = 'suggest'):
        cfg = get_config()
        bc = (cfg.get('backend') or {}).get('codex') or {}

        self.model = os.getenv('PYCODEX_CODEX_MODEL') or model or bc.get('model') or 'gpt-5-codex'
        self.approval_mode = os.getenv('PYCODEX_APPROVAL', approval_mode or bc.get('approval_mode') or 'suggest')
        self.base_cmd = os.getenv('PYCODEX_CODEX_CLI', bc.get('cli') or 'codex')

        # Optional behavior toggles
        self.use_files_arg = _truthy(os.getenv('PYCODEX_CODEX_FILES_ARG', str(bc.get('files_arg', False))))
        self.split_edit = _truthy(os.getenv('PYCODEX_CODEX_SPLIT_EDIT', str(bc.get('split_edit', True))))
        if which(self.base_cmd) is None:
            self._available = False
        else:
            self._available = True

    def _ensure_available(self):
        if not self._available and which(self.base_cmd) is None:
            raise BackendNotFoundError(f"Codex CLI not found: '{self.base_cmd}'. Set PYCODEX_CODEX_CLI or install the CLI.")

    def _run_exec(self, prompt: str, files: list[str] | None = None) -> CodexResult:
        import tempfile
        import os as _os

        self._ensure_available()
        context, file_log = read_files(files or [])
        full_prompt = prompt
        if context:
            full_prompt = f"{prompt}\n\n[CONTEXT]\n{context}"

        tmpf = tempfile.NamedTemporaryFile(prefix="pycodex_last_msg_", suffix=".txt", delete=False)
        tmp_path = tmpf.name
        tmpf.close()

        cmd: List[str] = [self.base_cmd, "exec"]
        if self.model:
            cmd += ["--model", self.model]
        cmd += ["--color", "never", "--skip-git-repo-check"]

        sandbox = _os.getenv("PYCODEX_CODEX_SANDBOX") or (get_config().get('backend') or {}).get('codex', {}).get('sandbox')
        if sandbox:
            cmd += ["--sandbox", str(sandbox)]

        cmd += ["--output-last-message", tmp_path]

        status, out, err = run_subprocess(cmd, input_text=full_prompt)
        try:
            if _os.path.exists(tmp_path):
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    last_msg = f.read()
            else:
                last_msg = out
        finally:
            try:
                _os.unlink(tmp_path)
            except Exception:
                pass

        if status != 0:
            raise ExecutionError(f"Codex CLI failed ({status}): {err.strip() or out.strip()}")

        code, text = parse_code_and_text(last_msg)
        return CodexResult(code=code, text=text, log=f"cmd={' '.join(cmd)}\n{file_log}")

    def generate(self, prompt: str, files: list[str] | None = None) -> CodexResult:
        return self._run_exec(prompt, files)

    def explain(self, code: str) -> CodexResult:
        prompt = (
            "Explain the following code in clear terms. Include purpose, key logic, and potential issues.\n\n"
            "```\n" + code + "\n```\n"
        )
        return self._run_exec(prompt)

    def edit(self, code: str, instructions: str) -> CodexResult:
        prompt = (
            "Edit the code per the instructions. Respond with the full, updated code in a fenced block.\n\n"
            "[INSTRUCTIONS]\n" + instructions + "\n\n[CODE]\n```\n" + code + "\n```\n"
        )
        return self._run_exec(prompt)

    def exec_command(self, command: str, safe: bool = True) -> CommandResult:
        status, out, err = exec_shell_command(command, safe=safe, approval_mode=self.approval_mode)
        return CommandResult(output=out, error=err, status_code=status)


def _truthy(val: Optional[str]) -> bool:
    if val is None:
        return False
    return str(val).strip().lower() in {"1", "true", "yes", "on"}
