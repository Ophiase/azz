from typing import Final

from azz.core.work_item import WorkItem
from azz.core.work_item.helper import Markdown, html_to_markdown

from .models import FieldDiff, LocalItem

ABSENT: Final = "—"

UPDATABLE_FIELDS: Final = frozenset({
    "title",
    "description",
    "state",
    "parent",
    "iteration",
})


def field_diffs(local_item: LocalItem, remote_item: WorkItem) -> tuple[FieldDiff, ...]:
    candidates = (
        _scalar_diff("title", local_item.title, remote_item.name),
        _scalar_diff("state", local_item.state, remote_item.state),
        _scalar_diff("type", local_item.item_type, remote_item.item_type),
        _scalar_diff("parent", local_item.parent, remote_item.parent_id),
        _scalar_diff("iteration", local_item.iteration, iteration_name(remote_item)),
        _description_diff(local_item.description, remote_item.description),
    )
    return tuple(diff for diff in candidates if diff is not None)


def normalize_markdown(text: Markdown | None) -> str:
    """Strip per-line whitespace and blank lines so the HTML round-trip
    survives comparison."""
    if not text:
        return ""
    stripped = (line.strip() for line in text.splitlines())
    return "\n".join(line for line in stripped if line)


def _scalar_diff(
    field_name: str, local_value: object | None, remote_value: object | None
) -> FieldDiff | None:
    if local_value is None:
        return None
    remote_text = str(remote_value) if remote_value is not None else ""
    if str(local_value) == remote_text:
        return None
    return FieldDiff(field_name, str(local_value), remote_text or ABSENT)


def _description_diff(
    local_description: Markdown | None, remote_description: Markdown | None
) -> FieldDiff | None:
    if local_description is None:
        return None
    local_text = normalize_markdown(local_description)
    remote_text = normalize_markdown(html_to_markdown(remote_description))
    if local_text == remote_text:
        return None
    return FieldDiff(
        "description", _line_count(local_text), _line_count(remote_text)
    )


def _line_count(text: str) -> str:
    if not text:
        return ABSENT
    count = len(text.splitlines())
    return f"{count} line{'' if count == 1 else 's'}"


def iteration_name(remote_item: WorkItem) -> str | None:
    iteration_path = remote_item.iteration_path
    if iteration_path is None or not iteration_path.value:
        return None
    return iteration_path.value.split("\\")[-1]
