from pathlib import Path
from typing import Final

BEGIN_MARKER: Final = "<!-- azz:begin -->"
END_MARKER: Final = "<!-- azz:end -->"


def install_block(document: Path, content: str) -> None:
    """Insert azz's section, replacing a previous install.

    Everything the developer wrote outside the markers is left untouched.
    """
    block = f"{BEGIN_MARKER}\n{content.strip()}\n{END_MARKER}\n"
    if not document.exists():
        document.write_text(block)
        return

    existing = document.read_text()
    if _has_block(existing):
        document.write_text(_replaced(existing, block))
        return
    document.write_text(f"{existing.rstrip()}\n\n{block}")


def remove_block(document: Path) -> bool:
    """Drop azz's section. Reports whether there was one to drop."""
    if not document.exists():
        return False
    existing = document.read_text()
    if not _has_block(existing):
        return False
    document.write_text(_replaced(existing, "").rstrip() + "\n")
    return True


def _has_block(existing: str) -> bool:
    return BEGIN_MARKER in existing and END_MARKER in existing


def _replaced(existing: str, block: str) -> str:
    before, _, remainder = existing.partition(BEGIN_MARKER)
    _, _, after = remainder.partition(END_MARKER)
    return f"{before.rstrip()}\n\n{block.rstrip()}{after}" if block else before + after
