from __future__ import annotations

import asyncio
from dataclasses import replace

from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Header, Label, ListItem, ListView
from textual.containers import Vertical

from azz.core.branch import branch_name
from azz.core.engine import Engine
from azz.core.timebox import Iteration
from azz.core.work_item import WorkItemState
from azz.core.work_item.work_item import WorkItem

_STATE_COLORS: dict[WorkItemState, str] = {
    WorkItemState.ACTIVE: "green",
    WorkItemState.NEW: "yellow",
    WorkItemState.RESOLVED: "cyan",
    WorkItemState.CLOSED: "grey50",
    WorkItemState.DESIGN: "blue",
}


class StatePickerScreen(ModalScreen[WorkItemState | None]):
    CSS = """
    StatePickerScreen {
        align: center middle;
    }
    #dialog {
        width: 30;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 1;
    }
    """

    BINDINGS = [("escape", "dismiss_none", "Cancel")]

    _STATES = (
        WorkItemState.NEW,
        WorkItemState.ACTIVE,
        WorkItemState.DESIGN,
        WorkItemState.RESOLVED,
        WorkItemState.CLOSED,
    )

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("[bold]Select State[/bold]")
            yield ListView(
                *[ListItem(Label(s.value), id=f"s-{s.value}") for s in self._STATES]
            )

    @on(ListView.Selected)
    def on_selected(self, event: ListView.Selected) -> None:
        raw_id = event.item.id or ""
        self.dismiss(WorkItemState.from_str(raw_id.removeprefix("s-")))

    def action_dismiss_none(self) -> None:
        self.dismiss(None)


class AzzTUI(App[None]):
    TITLE = "azz interactive"
    CSS = """
    DataTable { height: 1fr; }
    #filter-bar {
        height: 1;
        background: $surface;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("i", "cursor_up", "Up", show=False),
        Binding("k", "cursor_down", "Down", show=False),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("e", "edit_desc", "Edit"),
        Binding("r", "rename", "Rename"),
        Binding("s", "pick_state", "State"),
        Binding("plus", "timebox_next", "TB+"),
        Binding("minus", "timebox_prev", "TB-"),
        Binding("a", "toggle_closed", "[a]Closed"),
        Binding("A", "toggle_others", "[A]Others"),
        Binding("o", "toggle_others", "Others", show=False),
        Binding("b", "show_branch", "Branch"),
        Binding("R", "reload", "Reload"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, engine: Engine) -> None:
        super().__init__()
        self._engine = engine
        self._items: list[WorkItem] = []
        self._timeboxes: list[Iteration] = []
        self._include_closed = False
        self._show_others = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(cursor_type="row", id="table")
        yield Label("Loading...", id="filter-bar")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#table", DataTable)
        table.add_columns("ID", "TB", "Type", "State", "Name")
        self._load_all()

    @work(exclusive=True)
    async def _load_all(self) -> None:
        timeboxes, items = await asyncio.gather(
            asyncio.to_thread(self._engine.list_timeboxes),
            asyncio.to_thread(
                self._engine.list_work_items,
                states=self._get_states(),
                show_others=self._show_others,
            ),
        )
        self._timeboxes = list(timeboxes)
        self._items = list(items)
        self._refresh_table()

    def _get_states(self) -> frozenset[WorkItemState] | None:
        if self._include_closed:
            return frozenset({
                WorkItemState.ACTIVE,
                WorkItemState.NEW,
                WorkItemState.RESOLVED,
                WorkItemState.CLOSED,
            })
        return None

    def _refresh_table(self, preserve_cursor: bool = False) -> None:
        table = self.query_one("#table", DataTable)
        saved_row = table.cursor_row
        table.clear()
        for item in self._items:
            tb_num = item.iteration_path.optional_number if item.iteration_path else None
            tb = str(tb_num) if tb_num is not None else "─"
            color = _STATE_COLORS.get(item.state, "white")
            table.add_row(
                str(item.id),
                tb,
                str(item.item_type),
                Text(str(item.state), style=color),
                item.name,
                key=str(item.id),
            )
        if preserve_cursor and 0 <= saved_row < table.row_count:
            table.move_cursor(row=saved_row)
        self._update_filter_bar()

    def _update_filter_bar(self) -> None:
        closed = "[green]ON[/green]" if self._include_closed else "off"
        others = "[green]ON[/green]" if self._show_others else "off"
        self.query_one("#filter-bar", Label).update(
            f"[a] closed: {closed}  ·  [A] others: {others}  ·  {len(self._items)} items"
        )

    def _selected_item(self) -> WorkItem | None:
        table = self.query_one("#table", DataTable)
        if not self._items or table.row_count == 0:
            return None
        idx = table.cursor_row
        if 0 <= idx < len(self._items):
            return self._items[idx]
        return None

    # --- Navigation ---

    def action_cursor_up(self) -> None:
        self.query_one("#table", DataTable).action_cursor_up()

    def action_cursor_down(self) -> None:
        self.query_one("#table", DataTable).action_cursor_down()

    # --- Filter toggles ---

    def action_toggle_closed(self) -> None:
        self._include_closed = not self._include_closed
        self._load_all()

    def action_toggle_others(self) -> None:
        self._show_others = not self._show_others
        self._load_all()

    def action_reload(self) -> None:
        self._load_all()

    # --- Item actions ---

    async def action_edit_desc(self) -> None:
        item = self._selected_item()
        if item is None:
            return
        with self.suspend():
            self._engine.edit_work_item(item.id, edit_title=False)
        self._load_all()

    async def action_rename(self) -> None:
        item = self._selected_item()
        if item is None:
            return
        with self.suspend():
            self._engine.edit_work_item(item.id, edit_title=True)
        self._load_all()

    async def action_pick_state(self) -> None:
        item = self._selected_item()
        if item is None:
            return
        table = self.query_one("#table", DataTable)
        saved_row = table.cursor_row
        new_state: WorkItemState | None = await self.push_screen_wait(StatePickerScreen())
        if new_state is None:
            return
        await asyncio.to_thread(self._engine.update_work_item_state, item.id, new_state)
        if 0 <= saved_row < len(self._items):
            self._items[saved_row] = replace(self._items[saved_row], state=new_state)
        self._refresh_table(preserve_cursor=True)
        self.notify(f"State → {new_state.value}")

    async def action_timebox_next(self) -> None:
        await self._shift_timebox(+1)

    async def action_timebox_prev(self) -> None:
        await self._shift_timebox(-1)

    async def _shift_timebox(self, direction: int) -> None:
        item = self._selected_item()
        if item is None or not self._timeboxes:
            return
        current_num = (
            item.iteration_path.optional_number if item.iteration_path else None
        )
        if current_num is None:
            self.notify("Item has no timebox", severity="warning")
            return
        sorted_tb = sorted(
            self._timeboxes, key=lambda t: t.path.optional_number or 0
        )
        idx = next(
            (i for i, t in enumerate(sorted_tb) if t.path.optional_number == current_num),
            None,
        )
        if idx is None:
            self.notify("Current timebox not found in list", severity="warning")
            return
        new_idx = idx + direction
        if not (0 <= new_idx < len(sorted_tb)):
            self.notify("No timebox in that direction", severity="warning")
            return
        target_tb = sorted_tb[new_idx]
        await asyncio.to_thread(self._engine.set_timebox, item.id, target_tb)
        self.notify(f"TB → {target_tb.path.optional_number}")
        self._load_all()

    def action_show_branch(self) -> None:
        item = self._selected_item()
        if item is None:
            return
        self.notify(branch_name(item), title="Branch name", timeout=10)
