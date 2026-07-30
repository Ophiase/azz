from __future__ import annotations

from typing import Final

from rich.text import Text
from textual.widgets import DataTable

from azz.core.work_item.work_item import WorkItem
from azz.core.work_item.work_item_state import WorkItemState
from azz.plan.tracking import TrackingStatus
from azz.tui.plan_state import PlanState

_STATE_STYLES: Final[dict[str, str]] = {
    WorkItemState.ACTIVE.value: "bold green",
    WorkItemState.NEW.value: "yellow",
    WorkItemState.DESIGN.value: "bright_blue",
    WorkItemState.RESOLVED.value: "cyan",
    WorkItemState.CLOSED.value: "bright_black",
}

# Unlabelled single-glyph gutters: the selection marker, then the plan state.
_GUTTER_COLUMN_KEYS: Final[tuple[str, ...]] = ("marker", "plan")

_COLUMN_LABELS: Final[tuple[tuple[str, str], ...]] = (
    ("date", "Date"),
    ("id", "ID"),
    ("tb", "TB"),
    ("type", "Type"),
    ("state", "State"),
    ("name", "Name"),
)


class WorkItemTable(DataTable):
    DEFAULT_CSS = "WorkItemTable { height: 1fr; }"

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self._build_columns()

    @staticmethod
    def sortable_column_key(column_index: int) -> str | None:
        """
        Map a clicked header to a sort key, or None for a gutter column.

        The table owns this mapping so adding a gutter cannot silently shift
        the caller's column indices. `column_index` is used rather than
        `str(column_key)`, which does not round-trip cleanly in all Textual
        versions.
        """
        offset = column_index - len(_GUTTER_COLUMN_KEYS)
        if 0 <= offset < len(_COLUMN_LABELS):
            return _COLUMN_LABELS[offset][0]
        return None

    def _build_columns(
        self,
        sort_column: str = "date",
        sort_reverse: bool = True,
    ) -> None:
        arrow = "↓" if sort_reverse else "↑"
        for gutter_key in _GUTTER_COLUMN_KEYS:
            self.add_column("", key=gutter_key)
        for key, base_label in _COLUMN_LABELS:
            label = f"{base_label} {arrow}" if key == sort_column else base_label
            self.add_column(label, key=key)

    def populate(
        self,
        items: tuple[WorkItem, ...],
        *,
        preserve_cursor: bool = False,
        show_project: bool = False,
        selected_ids: frozenset[int] = frozenset(),
        sort_column: str = "date",
        sort_reverse: bool = True,
        plan_state: PlanState,
    ) -> None:
        saved_row = self.cursor_row
        self.clear(columns=True)
        self._build_columns(sort_column=sort_column, sort_reverse=sort_reverse)
        for item in items:
            self.add_row(
                *_item_row(
                    item,
                    show_project=show_project,
                    selected=item.id in selected_ids,
                    plan_status=plan_state.status(item.id),
                ),
                key=str(item.id),
            )
        if preserve_cursor and 0 <= saved_row < self.row_count:
            self.move_cursor(row=saved_row)


def _item_row(
    item: WorkItem,
    *,
    show_project: bool,
    selected: bool,
    plan_status: TrackingStatus,
) -> tuple[str | Text, ...]:
    timebox_number = (
        item.iteration_path.optional_number if item.iteration_path else None
    )
    color = _STATE_STYLES.get(item.state.value, "white")
    date = (
        f"{item.changed_date.day:02d}/{item.changed_date.month:02d}"
        if item.changed_date
        else "─────"
    )
    display_name = item.name if show_project else item.stripped_name
    marker = Text("◆", style="bold cyan") if selected else Text(" ")
    return (
        marker,
        Text(plan_status.glyph, style=plan_status.style),
        date,
        str(item.id),
        str(timebox_number) if timebox_number is not None else "─",
        str(item.item_type),
        Text(str(item.state), style=color),
        display_name,
    )
