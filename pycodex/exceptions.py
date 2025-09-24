class CodexError(Exception):
    """Base class for all PyCodex exceptions."""


class BackendNotFoundError(CodexError):
    """Raised if the specified backend is unsupported or CLI command not found."""


class ExecutionError(CodexError):
    """Raised if a shell command or backend execution fails."""

