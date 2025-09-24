---

# PyCodex / PyGemini CLI Python Module Specification

## Overview

This specification defines a Python module that wraps OpenAI Codex CLI or Gemini CLI, providing a unified interface for scripting code generation, editing, explanation, and command execution. The design allows swapping the backend (Codex or Gemini) without changing the user-facing API.

## Goals

* Unified interface for Codex and Gemini CLI.
* Scriptable from Python with simple API.
* Supports code generation, editing, explanation, and safe command execution.
* Configurable backend (Codex / Gemini), model, and approval mode.
* Extensible for prompt templates and project context.

## Module Structure

```
pycodex/
├─ __init__.py
├─ cli_wrapper.py       # Abstraction for CLI backend
├─ codex.py             # Codex specific logic
├─ gemini.py            # Gemini specific logic
├─ prompts.py           # Predefined prompt templates
├─ utils.py             # Helpers (file I/O, logging, sandboxing)
└─ exceptions.py        # Custom exceptions
```

## Core Classes

### CodexInterface

```python
class CodexInterface:
    def generate(self, prompt: str, files: list[str] = None) -> 'CodexResult':
        ...
    def explain(self, code: str) -> 'CodexResult':
        ...
    def edit(self, code: str, instructions: str) -> 'CodexResult':
        ...
    def exec_command(self, command: str, safe=True) -> 'CommandResult':
        ...
```

> This is the backend-agnostic interface. Both Codex and Gemini wrappers implement it.

### CodexBackend

```python
class CodexBackend(CodexInterface):
    def __init__(self, model='gpt-5-codex', approval_mode='suggest'):
        ...
```

> Wraps Codex CLI calls and implements the interface.

### GeminiBackend

```python
class GeminiBackend(CodexInterface):
    def __init__(self, model='gemini-1', approval_mode='suggest'):
        ...
```

> Wraps Gemini CLI calls and implements the interface.

### CodexResult

```python
class CodexResult:
    def __init__(self, code: str = '', text: str = '', log: str = ''):
        self.code = code
        self.text = text
        self.log = log
```

### CommandResult

```python
class CommandResult:
    def __init__(self, output: str, error: str, status_code: int):
        self.output = output
        self.error = error
        self.status_code = status_code
```

### PyCodex (Facade)

```python
class PyCodex:
    def __init__(self, backend: str = 'codex', model: str = None, approval_mode: str = 'suggest'):
        if backend.lower() == 'codex':
            self.backend = CodexBackend(model=model, approval_mode=approval_mode)
        elif backend.lower() == 'gemini':
            self.backend = GeminiBackend(model=model, approval_mode=approval_mode)
        else:
            raise ValueError('Unsupported backend')

    def generate(self, prompt: str, files: list[str] = None) -> CodexResult:
        return self.backend.generate(prompt, files)

    def explain(self, code: str) -> CodexResult:
        return self.backend.explain(code)

    def edit(self, code: str, instructions: str) -> CodexResult:
        return self.backend.edit(code, instructions)

    def exec_command(self, command: str, safe=True) -> CommandResult:
        return self.backend.exec_command(command, safe)
```

## Prompt Templates (prompts.py)

* `UNIT_TEST_GENERATOR` - Generate tests for a module.
* `DOCSTRING_EXPLAINER` - Explain function/class docstrings.
* `REFACTOR_GUIDE` - Suggest code refactors.

## Features

* **Backend Swap:** Easily switch between Codex and Gemini by changing the `backend` parameter.
* **Approval Modes:** 'suggest', 'auto-edit', 'full-auto' controlling edit/execution behavior.
* **File Context:** Provide file list for context during code generation/editing.
* **Interactive Session:** Optional `interactive()` method to start a session.
* **Safe Command Execution:** Optionally approve before executing shell commands.

## Exceptions

* `CodexError` - Base class for all module exceptions.
* `BackendNotFoundError` - Raised if specified backend is unsupported.
* `ExecutionError` - Raised if a command fails.

## Usage Example

```python
from pycodex import PyCodex

# Initialize facade with backend swap
coder = PyCodex(backend='gemini', model='gemini-1', approval_mode='suggest')

# Generate code
result = coder.generate('Write a Python function to reverse a string')
print(result.code)

# Explain code
explanation = coder.explain('def add(a, b): return a + b')
print(explanation.text)

# Edit code
edited = coder.edit('def add(a, b): return a', instructions='Fix the function to return the sum')
print(edited.code)

# Execute shell command safely
cmd_res = coder.exec_command('pytest tests/', safe=True)
print(cmd_res.output)
```

## Extensibility

* Add new backend: implement `CodexInterface`.
* Add new prompts: extend `prompts.py`.
* Advanced configuration via `~/.pycodex/config.toml`.

---

**End of Specification**
