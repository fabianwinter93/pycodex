from __future__ import annotations

import os
from typing import Optional

from .cli_wrapper import CodexInterface, CodexResult, CommandResult
from .exceptions import BackendNotFoundError, ExecutionError
from .utils import (
    build_cli_command,
    exec_shell_command,
    parse_code_and_text,
    read_files,
    run_subprocess,
    which,
)


class GeminiBackend(CodexInterface):
    def __init__(self, model: Optional[str] = 'gemini-1', approval_mode: str = 'suggest'):
        self.model = model
        self.approval_mode = approval_mode
        self.base_cmd = os.getenv('PYCODEX_GEMINI_CLI', 'gemini')
        if which(self.base_cmd) is None:
            self._available = False
        else:
            self._available = True

    def _ensure_available(self):
        if not self._available and which(self.base_cmd) is None:
            raise BackendNotFoundError(f"Gemini CLI not found: '{self.base_cmd}'. Set PYCODEX_GEMINI_CLI or install the CLI.")

    def _invoke(self, subcommand: str, payload: str, files: list[str] | None = None) -> CodexResult:
        self._ensure_available()
        context, file_log = read_files(files or [])
        full_input = payload
        if context:
            full_input = f"{payload}\n\n[CONTEXT]\n{context}"
        cmd = build_cli_command(self.base_cmd, subcommand, self.model, self.approval_mode)
        status, out, err = run_subprocess(cmd, input_text=full_input)
        if status != 0:
            raise ExecutionError(f"Gemini CLI failed ({status}): {err.strip() or out.strip()}")
        code, text = parse_code_and_text(out)
        return CodexResult(code=code, text=text, log=f"cmd={' '.join(cmd)}\n{file_log}")

    def generate(self, prompt: str, files: list[str] | None = None) -> CodexResult:
        return self._invoke('generate', prompt, files)

    def explain(self, code: str) -> CodexResult:
        return self._invoke('explain', code)

    def edit(self, code: str, instructions: str) -> CodexResult:
        payload = f"[INSTRUCTIONS]\n{instructions}\n\n[CODE]\n{code}"
        return self._invoke('edit', payload)

    def exec_command(self, command: str, safe: bool = True) -> CommandResult:
        status, out, err = exec_shell_command(command, safe=safe, approval_mode=self.approval_mode)
        return CommandResult(output=out, error=err, status_code=status)
