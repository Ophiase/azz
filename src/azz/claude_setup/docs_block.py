from pathlib import Path
from typing import Final

BEGIN_MARKER: Final = "<!-- azz:begin -->"
END_MARKER: Final = "<!-- azz:end -->"


def install_docs(claude_md: Path, content: str) -> None:
    """Insert the profile docs into CLAUDE.md, replacing a previous install.

    Everything the user wrote outside the markers is left untouched.
    """
    block = f"{BEGIN_MARKER}\n{content.strip()}\n{END_MARKER}\n"
    if not claude_md.exists():
        claude_md.write_text(block)
        return

    existing = claude_md.read_text()
    if BEGIN_MARKER in existing and END_MARKER in existing:
        claude_md.write_text(_replace_block(existing, block))
        return
    claude_md.write_text(f"{existing.rstrip()}\n\n{block}")


def _replace_block(existing: str, block: str) -> str:
    before, _, remainder = existing.partition(BEGIN_MARKER)
    _, _, after = remainder.partition(END_MARKER)
    return f"{before}{block.rstrip()}{after}"
