from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar, Final

from rich.style import Style
from rich.text import Text
from textual.widgets import DataTable

from azz.core.work_item.work_item import WorkItem
from azz.core.work_item.work_item_state import WorkItemState
from azz.plan.tracking import TrackingStatus
from azz.tui.column_widths import Cell, column_widths
from azz.tui.plan_state import PlanState
from azz.tui.priority_tint import PriorityTint

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
    ("tb", "TB"),
    ("type", "Type"),
    ("state", "S"),
    ("priority", "P"),
    ("name", "Name"),
    ("id", "ID"),
)


class WorkItemTable(DataTable):
    DEFAULT_CSS = """
    WorkItemTable { height: 1fr; }
    WorkItemTable > .work-table--critical { background: $error 18%; }
    WorkItemTable > .work-table--minor { background: $primary 10%; }
    """
    COMPONENT_CLASSES: ClassVar = DataTable.COMPONENT_CLASSES | {
        tint.value for tint in PriorityTint
    }
    _row_tints: tuple[PriorityTint | None, ...] = ()

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self._build_columns(rows=())

    def _get_row_style(self, row_index: int, base_style: Style) -> Style:
        row_style = super()._get_row_style(row_index, base_style)
        in_body = 0 <= row_index < len(self._row_tints)
        tint = self._row_tints[row_index] if in_body else None
        if tint is None:
            return row_style
        return row_style + self.get_component_styles(tint.value).rich_style

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
        rows: Sequence[Sequence[Cell]],
        sort_column: str = "date",
        sort_reverse: bool = True,
    ) -> None:
        arrow = "↓" if sort_reverse else "↑"
        keys = (*_GUTTER_COLUMN_KEYS, *(key for key, _ in _COLUMN_LABELS))
        labels = (
            *("" for _ in _GUTTER_COLUMN_KEYS),
            *(
                f"{base_label} {arrow}" if key == sort_column else base_label
                for key, base_label in _COLUMN_LABELS
            ),
        )
        for key, label, width in zip(
            keys, labels, column_widths(labels, rows), strict=True
        ):
            self.add_column(label, key=key, width=width)

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
        rows = tuple(
            _item_row(
                item,
                show_project=show_project,
                selected=item.id in selected_ids,
                plan_status=plan_state.status(item.id),
            )
            for item in items
        )
        self.clear(columns=True)
        self._row_tints = tuple(PriorityTint.of(item.priority) for item in items)
        self._build_columns(rows, sort_column=sort_column, sort_reverse=sort_reverse)
        for item, row in zip(items, rows, strict=True):
            self.add_row(*row, key=str(item.id))
        if preserve_cursor and 0 <= saved_row < self.row_count:
            self.move_cursor(row=saved_row)


def _item_row(
    item: WorkItem,
    *,
    show_project: bool,
    selected: bool,
    plan_status: TrackingStatus,
) -> tuple[Cell, ...]:
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
        str(timebox_number) if timebox_number is not None else "─",
        item.item_type.short_label,
        Text(item.state.initial, style=color),
        str(int(item.priority)) if item.priority is not None else "─",
        display_name,
        str(item.id),
    )
