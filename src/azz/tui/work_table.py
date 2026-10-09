from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar, Final

from rich.style import Style
from rich.text import Text
from textual.widgets import DataTable

from azz.core.work_item.work_item_state import WorkItemState
from azz.plan.tracking import TrackingStatus
from azz.tui.column_widths import Cell, column_widths
from azz.tui.plan_state import PlanState
from azz.tui.row_tint import RowTint
from azz.tui.rows import DisplayRow

_STATE_STYLES: Final[dict[str, str]] = {
    WorkItemState.ACTIVE.value: "bold green",
    WorkItemState.NEW.value: "yellow",
    WorkItemState.DESIGN.value: "bright_blue",
    WorkItemState.RESOLVED.value: "",
    WorkItemState.CLOSED.value: "",
}

# Unlabelled single-glyph gutters: the selection marker, then the plan state.
_GUTTER_COLUMN_KEYS: Final[tuple[str, ...]] = ("marker", "plan")

_COLUMN_LABELS: Final[tuple[tuple[str, str], ...]] = (
    ("date", "Date"),
    ("type", "Type"),
    ("state", "S"),
    ("name", "Name"),
    ("tb", "TB"),
    ("priority", "P"),
    ("id", "ID"),
)


class WorkItemTable(DataTable):
    DEFAULT_CSS = """
    WorkItemTable { height: 1fr; }
    WorkItemTable > .work-table--critical { background: $error 18%; }
    WorkItemTable > .work-table--minor { background: $primary 10%; }
    WorkItemTable > .work-table--done { color: $foreground 35%; }
    """
    COMPONENT_CLASSES: ClassVar = DataTable.COMPONENT_CLASSES | {
        tint.value for tint in RowTint
    }
    _row_tints: tuple[RowTint | None, ...] = ()
    _row_styles: tuple[Style, ...] = ()

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self._build_columns(rows=())

    def _get_row_style(self, row_index: int, base_style: Style) -> Style:
        row_style = super()._get_row_style(row_index, base_style)
        in_body = 0 <= row_index < len(self._row_tints)
        if not in_body:
            return row_style
        tint = self._row_tints[row_index]
        if tint is not None:
            row_style += self.get_component_styles(tint.value).rich_style
        return row_style + self._row_styles[row_index]

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
        display_rows: Sequence[DisplayRow],
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
                display_row,
                show_project=show_project,
                selected=display_row.item.id in selected_ids,
                plan_status=plan_state.status(display_row.item.id),
            )
            for display_row in display_rows
        )
        self.clear(columns=True)
        self._row_tints = tuple(
            RowTint.of_item(display_row.item) for display_row in display_rows
        )
        self._row_styles = tuple(display_row.style for display_row in display_rows)
        self._build_columns(rows, sort_column=sort_column, sort_reverse=sort_reverse)
        for display_row, row in zip(display_rows, rows, strict=True):
            self.add_row(*row, key=str(display_row.item.id))
        if preserve_cursor and 0 <= saved_row < self.row_count:
            self.move_cursor(row=saved_row)


def _item_row(
    display_row: DisplayRow,
    *,
    show_project: bool,
    selected: bool,
    plan_status: TrackingStatus,
) -> tuple[Cell, ...]:
    item = display_row.item
    timebox_number = (
        item.iteration_path.optional_number if item.iteration_path else None
    )
    color = _STATE_STYLES.get(item.state.value, "white")
    date = (
        f"{item.changed_date.day:02d}/{item.changed_date.month:02d}"
        if item.changed_date
        else "─────"
    )
    name = item.name if show_project else item.stripped_name
    marker = Text("◆", style="bold cyan") if selected else Text(" ")
    return (
        marker,
        Text(plan_status.glyph, style=plan_status.style),
        date,
        item.item_type.short_label,
        Text(item.state.initial, style=color),
        _name_cell(display_row, name),
        str(timebox_number) if timebox_number is not None else "─",
        str(int(item.priority)) if item.priority is not None else "─",
        str(item.id),
    )


def _name_cell(display_row: DisplayRow, name: str) -> Text:
    """The name between its tree branch and the count a fold hides."""
    hidden = display_row.folded_descendants
    fold_hint = f"  +{hidden}" if hidden else ""
    return Text.assemble((display_row.branch, "dim"), name, (fold_hint, "dim"))
