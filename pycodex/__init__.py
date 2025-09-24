from __future__ import annotations

from typing import Optional

from .cli_wrapper import CodexResult, CommandResult
from .codex import CodexBackend
from .gemini import GeminiBackend
from .exceptions import CodexError, BackendNotFoundError, ExecutionError


class PyCodex:
    def __init__(self, backend: str = 'codex', model: Optional[str] = None, approval_mode: str = 'suggest'):
        backend_lc = backend.lower()
        if backend_lc == 'codex':
            self.backend = CodexBackend(model=model or 'gpt-5-codex', approval_mode=approval_mode)
        elif backend_lc == 'gemini':
            self.backend = GeminiBackend(model=model or 'gemini-1', approval_mode=approval_mode)
        else:
            raise ValueError('Unsupported backend')

    def generate(self, prompt: str, files: list[str] | None = None) -> CodexResult:
        return self.backend.generate(prompt, files)

    def explain(self, code: str) -> CodexResult:
        return self.backend.explain(code)

    def edit(self, code: str, instructions: str) -> CodexResult:
        return self.backend.edit(code, instructions)

    def exec_command(self, command: str, safe: bool = True) -> CommandResult:
        return self.backend.exec_command(command, safe)

    def interactive(self):
        print("PyCodex interactive session. Type 'exit' to quit.")
        while True:
            try:
                line = input("pycodex> ").strip()
            except EOFError:
                print()
                break
            if not line:
                continue
            if line in {"exit", "quit"}:
                break
            if line.startswith('!'):
                cmd = line[1:].strip()
                res = self.exec_command(cmd, safe=True)
                print(res.output or res.error)
                continue
            res = self.generate(line)
            print(res.code or res.text)

__all__ = [
    'PyCodex',
    'CodexResult',
    'CommandResult',
    'CodexError',
    'BackendNotFoundError',
    'ExecutionError',
]
