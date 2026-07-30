import re
from typing import Final

from azz.core.work_item import WorkItem

MAX_SLUG_WORDS: Final = 6


def intent_file_name(work_item: WorkItem, max_words: int = MAX_SLUG_WORDS) -> str:
    """`7651-langfuse-trace-expected-output.md` — the id keeps it unique,
    the slug keeps it readable."""
    return f"{work_item.id}-{_slug(work_item.stripped_name, max_words)}.md"


def _slug(text: str, max_words: int) -> str:
    words = re.findall(r"[a-zA-Z0-9]+", text)[:max_words]
    return "-".join(word.lower() for word in words) or "task"
