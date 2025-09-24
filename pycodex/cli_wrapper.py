from __future__ import annotations

from abc import ABC, abstractmethod


class CodexResult:
    def __init__(self, code: str = '', text: str = '', log: str = ''):
        self.code = code
        self.text = text
        self.log = log


class CommandResult:
    def __init__(self, output: str, error: str, status_code: int):
        self.output = output
        self.error = error
        self.status_code = status_code


class CodexInterface(ABC):
    @abstractmethod
    def generate(self, prompt: str, files: list[str] | None = None) -> CodexResult:
        ...

    @abstractmethod
    def explain(self, code: str) -> CodexResult:
        ...

    @abstractmethod
    def edit(self, code: str, instructions: str) -> CodexResult:
        ...

    @abstractmethod
    def exec_command(self, command: str, safe: bool = True) -> CommandResult:
        ...
