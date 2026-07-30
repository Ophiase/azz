from collections.abc import Sequence
from pathlib import Path

from rich.markup import escape

from azz.core.work_item.work_item_type import WorkItemType

from .models import (
    ApplyOutcome,
    Change,
    Changeset,
    ChangeType,
    FetchOutcome,
    FetchStatus,
    LocalItem,
)

LABEL_WIDTH = 8
DIFF_INDENT = " " * (LABEL_WIDTH + 4)
REMOTE_MOVED_NOTICE = "⚠ remote changed since the last fetch"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def render_changeset(changeset: Changeset) -> str:
    return "\n".join(render_change(change) for change in changeset.changes)


def render_change(change: Change) -> str:
    lines = [_header(change)]
    if change.remote_moved:
        lines.append(f"{DIFF_INDENT}[magenta]{REMOTE_MOVED_NOTICE}[/magenta]")
    lines.extend(f"{DIFF_INDENT}{diff.render()}" for diff in change.field_diffs)
    return "\n".join(lines)


def render_fetch_outcome(outcome: FetchOutcome) -> str:
    status = outcome.status
    label = escape(f"[{status.label}]".ljust(LABEL_WIDTH))
    reason = f" [yellow]({escape(outcome.reason)})[/yellow]" if outcome.reason else ""
    return (
        f"[{status.style}]{label}[/{status.style}] "
        f"{escape(display_path(outcome.path))} "
        f"[grey50]#{outcome.work_item.id}[/grey50]{reason}"
    )


def render_fetch_summary(outcomes: Sequence[FetchOutcome]) -> str:
    counts = ", ".join(
        f"{sum(1 for outcome in outcomes if outcome.status is status)} "
        f"{status.label.lower()}"
        for status in FetchStatus
    )
    return f"[bold]{counts}[/bold]"


def render_summary(changeset: Changeset) -> str:
    counts = ", ".join(
        f"{len(changeset.of_type(change_type))} {change_type.label.lower()}"
        for change_type in ChangeType
    )
    return f"[bold]{counts}[/bold]"


def render_prompt(change: Change) -> str:
    local_item = change.local_item
    location = display_path(local_item.path)
    if change.change_type is ChangeType.CREATE:
        target = creation_target(local_item)
        return f'Create {target} "{local_item.title}" ({location})?'
    fields = ", ".join(sorted(change.changed_field_names))
    warning = f"{REMOTE_MOVED_NOTICE} — " if change.remote_moved else ""
    return f"{warning}Update #{local_item.item_id} ({location}) — {fields}?"


def render_outcome(outcome: ApplyOutcome) -> str:
    marker, style = ("→", "green") if outcome.succeeded else ("✗", "red")
    return f"  [{style}]{marker} {escape(outcome.message)}[/{style}]"


def creation_target(local_item: LocalItem) -> str:
    item_type = local_item.item_type or WorkItemType.TASK
    parent = f" under #{local_item.parent}" if local_item.parent else ""
    return f"{item_type}{parent}"


def _header(change: Change) -> str:
    change_type = change.change_type
    label = escape(f"[{change_type.label}]".ljust(LABEL_WIDTH))
    location = escape(display_path(change.local_item.path))
    return (
        f"[{change_type.style}]{label}[/{change_type.style}] "
        f"{location}{_identifier(change)} {_summary(change)}"
    ).rstrip()


def _identifier(change: Change) -> str:
    item_id = change.local_item.item_id
    return f" (#{item_id})" if item_id is not None else ""


def _summary(change: Change) -> str:
    match change.change_type:
        case ChangeType.CREATE:
            return f"→ will create {escape(creation_target(change.local_item))}"
        case ChangeType.NOOP:
            return "[grey50]✓ in sync[/grey50]"
        case ChangeType.GONE:
            return "[red]→ item not found on remote[/red]"
        case ChangeType.UPDATE:
            return ""
