import os
import re
import pandas as pd
from tools.security import MAX_ROWS, validate_upload_size


def _sanitize_filename(name: str) -> str:
    """
    Return a safe filename derived from *name*.

    - Strips leading dots and path separators.
    - Replaces any character that is not alphanumeric, a hyphen,
      an underscore, or a period with an underscore.
    - Falls back to 'upload.csv' if the result would be empty.
    """
    # Remove path components so callers cannot write outside uploads/
    basename = os.path.basename(name)
    # Keep only safe characters
    safe = re.sub(r"[^\w.\-]", "_", basename)
    # Strip leading dots (hidden file trick on Unix)
    safe = safe.lstrip(".")
    return safe if safe else "upload.csv"


def save_and_load_csv(uploaded_file) -> tuple:
    """
    Saves the uploaded Streamlit file to the uploads/ directory
    and returns a tuple (DataFrame, file_path, warnings).

    Security checks applied:
      1. Filename sanitization — strips path traversal characters.
      2. File size cap         — rejects files larger than MAX_FILE_SIZE_BYTES.
      3. CSV validity check    — file must be parseable by pandas.
      4. Row count cap         — truncates DataFrames exceeding MAX_ROWS rows
                                 and returns a user-visible warning string.

    Returns:
        (df, file_path, warnings) where ``warnings`` is a list of strings
        (may be empty) describing any data that was silently modified.
    """
    warnings: list[str] = []

    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    safe_name = _sanitize_filename(uploaded_file.name)
    file_path = os.path.join("uploads", safe_name)

    # --- Security check 1: File size cap (delegated to security module) ---
    file_bytes = uploaded_file.getbuffer()
    validate_upload_size(len(file_bytes))  # raises ValueError if too large

    # Save file physically
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # --- Security check 2: CSV validity check ---
    try:
        df = pd.read_csv(file_path, nrows=MAX_ROWS + 1)
    except Exception as exc:
        os.remove(file_path)  # clean up invalid file
        raise ValueError(f"File does not appear to be a valid CSV: {exc}") from exc

    # --- Security check 3: Row count cap with user warning ---
    if len(df) > MAX_ROWS:
        df = df.iloc[:MAX_ROWS]
        warnings.append(
            f"⚠️ Your file has more than {MAX_ROWS:,} rows. "
            f"Only the first {MAX_ROWS:,} rows have been loaded."
        )

    return df, file_path, warnings
