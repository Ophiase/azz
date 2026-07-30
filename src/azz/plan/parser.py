from collections.abc import Sequence
from pathlib import Path
from typing import Any, Final

from pydantic import ValidationError

from azz.core.work_item import WorkItemState
from azz.core.work_item.work_item_type import WorkItemType

from .errors import IntentFileError
from .frontmatter import Frontmatter
from .models import LocalItem

RETIRED_FIELDS: Final = frozenset({"remote_changed_date"})
"""Accepted and ignored for one release. `.azz/cache/` replaced them: the merge
base makes a tool-managed timestamp in a human-readable file unnecessary."""

KNOWN_FIELDS: Final = frozenset({
    "item_id",
    "title",
    "state",
    "type",
    "parent",
    "iteration",
    *RETIRED_FIELDS,
})


def parse_intent_files(paths: Sequence[Path]) -> tuple[LocalItem, ...]:
    return tuple(parse_intent_file(path) for path in paths)


def parse_intent_file(path: Path) -> LocalItem:
    try:
        frontmatter = Frontmatter.from_text(path.read_text())
    except (OSError, ValueError) as error:
        raise IntentFileError(path, str(error)) from error
    return _build_local_item(path, frontmatter)


def _build_local_item(path: Path, frontmatter: Frontmatter) -> LocalItem:
    metadata = frontmatter.metadata
    _reject_unknown_fields(path, metadata)
    try:
        return LocalItem(
            path=path,
            item_id=metadata.get("item_id"),
            title=metadata.get("title"),
            state=_optional_state(metadata.get("state")),
            item_type=_optional_type(metadata.get("type")),
            parent=metadata.get("parent"),
            iteration=_optional_text(metadata.get("iteration")),
            description=frontmatter.body or None,
        )
    except (ValidationError, ValueError) as error:
        raise IntentFileError(path, str(error)) from error


def _reject_unknown_fields(path: Path, metadata: dict[str, Any]) -> None:
    unknown = sorted(set(metadata) - KNOWN_FIELDS)
    if unknown:
        raise IntentFileError(path, f"unknown frontmatter fields: {', '.join(unknown)}")


def _optional_state(value: Any) -> WorkItemState | None:
    return WorkItemState.from_user_input(str(value)) if value is not None else None


def _optional_type(value: Any) -> WorkItemType | None:
    return WorkItemType.from_user_input(str(value)) if value is not None else None


def _optional_text(value: Any) -> str | None:
    return str(value) if value is not None else None
