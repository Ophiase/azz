from __future__ import annotations

from typing import Final

from rich.text import Text
from textual.widgets import DataTable

from azz.core.work_item.work_item import WorkItem
from azz.core.work_item.work_item_state import WorkItemState

_STATE_STYLES: Final[dict[str, str]] = {
    WorkItemState.ACTIVE.value: "bold green",
    WorkItemState.NEW.value: "yellow",
    WorkItemState.DESIGN.value: "bright_blue",
    WorkItemState.RESOLVED.value: "cyan",
    WorkItemState.CLOSED.value: "bright_black",
}


class WorkItemTable(DataTable):
    DEFAULT_CSS = "WorkItemTable { height: 1fr; }"

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("", "Date", "ID", "TB", "Type", "State", "Name")

    def populate(
        self,
        items: tuple[WorkItem, ...],
        *,
        preserve_cursor: bool = False,
        show_project: bool = False,
        selected_ids: frozenset[int] = frozenset(),
    ) -> None:
        saved_row = self.cursor_row
        self.clear()
        for item in items:
            self.add_row(
                *_item_row(
                    item,
                    show_project=show_project,
                    selected=item.id in selected_ids,
                ),
                key=str(item.id),
            )
        if preserve_cursor and 0 <= saved_row < self.row_count:
            self.move_cursor(row=saved_row)


def _item_row(
    item: WorkItem, *, show_project: bool, selected: bool
) -> tuple[Text, str, str, str, str, Text, str]:
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
        date,
        str(item.id),
        str(timebox_number) if timebox_number is not None else "─",
        str(item.item_type),
        Text(str(item.state), style=color),
        display_name,
    )
