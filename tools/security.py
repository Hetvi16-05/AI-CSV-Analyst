"""
tools/security.py
-----------------
Centralised security helpers for the AI CSV Analyst app.

Provides:
  - validate_csv_path()   : Path traversal guard for tool calls
  - sanitize_user_input() : Prompt injection + input hygiene
  - MAX_QUERIES_PER_SESSION : Session rate-limit constant
  - MAX_FILE_SIZE_BYTES     : Upload size cap constant
  - MAX_ROWS                : DataFrame row cap constant
"""

import os


def validate_csv_path(csv_path: str) -> str:
    """
    Guard against path traversal attacks.

    Resolves the given path to an absolute path and verifies it lives
    inside the project's ``uploads/`` directory.  Raises ``ValueError``
    if the path escapes the allowed directory so callers can return a
    safe error message instead of reading arbitrary files.

    Args:
        csv_path: The path string supplied by the LLM or the user.

    Returns:
        The resolved absolute path (str) when it is safe.

    Raises:
        ValueError: If the path resolves outside ``uploads/``.
    """
    # Resolve both sides to real absolute paths (handles ../ tricks)
    uploads_dir = os.path.realpath(
        os.path.join(os.path.dirname(__file__), "..", "uploads")
    )
    resolved = os.path.realpath(csv_path)

    if not resolved.startswith(uploads_dir + os.sep) and resolved != uploads_dir:
        raise ValueError(
            f"Access denied: '{csv_path}' is outside the permitted uploads directory."
        )

    if not resolved.endswith(".csv"):
        raise ValueError(
            f"Access denied: only .csv files are permitted, got '{os.path.basename(resolved)}'."
        )

    return resolved


import re  # noqa: E402 — placed after validate_csv_path for readability

# Phrases commonly used in prompt-injection attacks
_INJECTION_PATTERNS = re.compile(
    r"(ignore (all |previous |above |prior )?(instructions?|prompts?|rules?|context))|"
    r"(you are now|act as|pretend (to be|you are)|new (persona|role|identity))|"
    r"(disregard|forget|override|bypass).{0,30}(instruction|system|rule)|"
    r"(jailbreak|DAN mode|developer mode)",
    re.IGNORECASE,
)

MAX_INPUT_LENGTH = 2_000  # characters


def sanitize_user_input(text: str) -> tuple[str, list[str]]:
    """
    Clean and validate user-supplied chat text before passing it to the LLM.

    Performs the following checks in order:
    1. Strips null bytes and ASCII control characters (except newline/tab).
    2. Truncates input exceeding ``MAX_INPUT_LENGTH`` characters.
    3. Scans for prompt-injection phrases and flags them.

    Args:
        text: Raw user input from the chat widget.

    Returns:
        A tuple ``(cleaned_text, warnings)`` where ``warnings`` is a list
        of human-readable warning strings (empty when input is clean).
    """
    warnings: list[str] = []

    # 1. Strip dangerous control characters (keep \n and \t)
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # 2. Enforce length cap
    if len(cleaned) > MAX_INPUT_LENGTH:
        cleaned = cleaned[:MAX_INPUT_LENGTH]
        warnings.append(
            f"⚠️ Your message was truncated to {MAX_INPUT_LENGTH} characters."
        )

    # 3. Detect prompt injection attempts
    if _INJECTION_PATTERNS.search(cleaned):
        warnings.append(
            "⚠️ Your message appears to contain instruction-override phrases. "
            "The agent will only answer questions about your CSV data."
        )

    return cleaned, warnings


# ---------------------------------------------------------------------------
# Application-wide security constants
# ---------------------------------------------------------------------------

# Maximum number of agent queries allowed per Streamlit session.
# Prevents a single user from hammering the local Ollama model.
MAX_QUERIES_PER_SESSION: int = 30

# Maximum file size accepted for CSV uploads (50 MB).
MAX_FILE_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB

# Maximum number of rows loaded from a CSV into pandas.
# Protects against out-of-memory attacks with huge files.
MAX_ROWS: int = 500_000
