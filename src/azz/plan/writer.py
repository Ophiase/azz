from collections.abc import Sequence
from pathlib import Path

from .errors import IntentFileError
from .frontmatter import DELIMITER, quote_scalar


def write_back(
    path: Path,
    item_id: int | None = None,
    title: str | None = None,
) -> None:
    """
    Make the intent file canonical after a remote operation.

    Only the supplied frontmatter keys are rewritten — the rest of the file,
    body included, is preserved verbatim.
    """
    lines = path.read_text().splitlines()
    closing_index = _closing_delimiter_index(path, lines)
    block = lines[1:closing_index]
    for key, value in (("item_id", item_id), ("title", title)):
        if value is not None:
            block = _upsert(block, key, quote_scalar(str(value)))
    updated = [lines[0], *block, *lines[closing_index:]]
    path.write_text("\n".join(updated) + "\n")


def _closing_delimiter_index(path: Path, lines: Sequence[str]) -> int:
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == DELIMITER:
            return index
    raise IntentFileError(path, f"unterminated frontmatter: no closing '{DELIMITER}'")


def _upsert(block: Sequence[str], key: str, value: str) -> list[str]:
    entry = f"{key}: {value}"
    prefix = f"{key}:"
    if any(line.strip().startswith(prefix) for line in block):
        return [entry if line.strip().startswith(prefix) else line for line in block]
    return [entry, *block]
