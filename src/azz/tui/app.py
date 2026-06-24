from __future__ import annotations

import asyncio
from dataclasses import replace
from typing import ClassVar, Final

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Footer, Header

from azz.core.branch import branch_name
from azz.core.clipboard import copy_to_clipboard
from azz.core.engine import Engine
from azz.core.timebox import Iteration
from azz.core.work_item import WorkItemState
from azz.core.work_item.work_item import WorkItem
from azz.tui.create_screen import CreateScreen, NewTaskData
from azz.tui.detail_screen import DetailScreen
from azz.tui.filter_bar import FilterBar
from azz.tui.rename_screen import RenameScreen
from azz.tui.state_picker import StatePickerScreen
from azz.tui.timebox_nav import adjacent_timebox
from azz.tui.work_table import WorkItemTable

_ALL_STATES: Final = frozenset({
    WorkItemState.ACTIVE,
    WorkItemState.NEW,
    WorkItemState.DESIGN,
    WorkItemState.RESOLVED,
    WorkItemState.CLOSED,
})

_OPEN_STATES: Final = frozenset({
    WorkItemState.ACTIVE,
    WorkItemState.NEW,
    WorkItemState.DESIGN,
})


class AzzTUI(App[None]):
    TITLE = "azz interactive"
    CSS = "Screen { background: transparent; }"

    BINDINGS: ClassVar = [
        Binding("k", "cursor_up", "Up", show=False),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("n", "new_task", "New"),
        Binding("e", "edit_desc", "Edit"),
        Binding("r", "rename", "Rename"),
        Binding("s", "pick_state", "State"),
        Binding("plus", "timebox_next", "TB+"),
        Binding("minus", "timebox_prev", "TB-"),
        Binding("a", "toggle_closed", "[a]Closed"),
        Binding("A", "toggle_others", "[A]Others"),
        Binding("o", "toggle_others", "Others", show=False),
        Binding("c", "toggle_current_timebox", "[c]Current"),
        Binding("p", "toggle_project", "[p]Project"),
        Binding("b", "show_branch", "Branch"),
        Binding("R", "reload", "Reload"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, engine: Engine) -> None:
        super().__init__()
        self._engine = engine
        self._all_items: tuple[WorkItem, ...] = ()
        self._items: tuple[WorkItem, ...] = ()
        self._timeboxes: tuple[Iteration, ...] = ()
        self._include_closed: bool = False
        self._show_others: bool = False
        self._current_timebox_only: bool = False
        self._show_project: bool = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield WorkItemTable(id="table")
        yield FilterBar("Loading...", id="filter-bar")
        yield Footer()

    def on_mount(self) -> None:
        self.theme = "rose-pine-dawn"
        self._fetch_items()

    @work(exclusive=True)
    async def _fetch_items(self) -> None:
        self._timeboxes, self._all_items = await asyncio.gather(
            asyncio.to_thread(self._engine.list_timeboxes),
            asyncio.to_thread(
                self._engine.list_work_items,
                states=_ALL_STATES,
                show_others=self._show_others,
            ),
        )
        self._apply_filters()

    def _current_timebox_number(self) -> int | None:
        return next(
            (
                tb.path.optional_number
                for tb in self._timeboxes
                if tb.is_current
            ),
            None,
        )

    def _apply_filters(self) -> None:
        visible_states = _ALL_STATES if self._include_closed else _OPEN_STATES
        items = tuple(
            item for item in self._all_items if item.state in visible_states
        )
        if self._current_timebox_only:
            current_number = self._current_timebox_number()
            if current_number is not None:
                items = tuple(
                    item for item in items
                    if item.iteration_path
                    and item.iteration_path.optional_number == current_number
                )
        self._items = tuple(sorted(
            items,
            key=lambda item: (
                item.changed_date.timestamp() if item.changed_date else 0.0
            ),
            reverse=True,
        ))
        self._refresh_view()

    def _refresh_view(self, *, preserve_cursor: bool = False) -> None:
        self.query_one(WorkItemTable).populate(
            self._items,
            preserve_cursor=preserve_cursor,
            show_project=self._show_project,
        )
        self.query_one(FilterBar).update_filters(
            include_closed=self._include_closed,
            show_others=self._show_others,
            current_timebox_only=self._current_timebox_only,
            show_project=self._show_project,
            item_count=len(self._items),
        )

    def _cursor_item(self) -> WorkItem | None:
        cursor_row = self.query_one(WorkItemTable).cursor_row
        if self._items and 0 <= cursor_row < len(self._items):
            return self._items[cursor_row]
        return None

    # --- Navigation ---

    def action_cursor_up(self) -> None:
        self.query_one(WorkItemTable).action_cursor_up()

    def action_cursor_down(self) -> None:
        self.query_one(WorkItemTable).action_cursor_down()

    @on(DataTable.RowSelected)
    def on_row_selected(self) -> None:
        self.action_show_detail()

    # --- Filter toggles (client-side — no network call) ---

    def action_toggle_closed(self) -> None:
        self._include_closed = not self._include_closed
        self._apply_filters()

    def action_toggle_current_timebox(self) -> None:
        self._current_timebox_only = not self._current_timebox_only
        self._apply_filters()

    def action_toggle_project(self) -> None:
        self._show_project = not self._show_project
        self._refresh_view()

    # --- Filter toggles (server-side — refetch needed) ---

    def action_toggle_others(self) -> None:
        self._show_others = not self._show_others
        self._fetch_items()

    def action_reload(self) -> None:
        self._fetch_items()

    # --- Item actions ---

    async def action_edit_desc(self) -> None:
        item = self._cursor_item()
        if item is None:
            return
        with self.suspend():
            self._engine.edit_work_item(item.id, edit_title=False)
        self._fetch_items()

    @work
    async def action_show_detail(self) -> None:
        item = self._cursor_item()
        if item is None:
            return
        full_item = await asyncio.to_thread(self._engine.get_workitem, item.id)
        await self.push_screen_wait(DetailScreen(full_item))

    @work
    async def action_rename(self) -> None:
        item = self._cursor_item()
        if item is None:
            return
        new_title: str | None = await self.push_screen_wait(
            RenameScreen(item.stripped_name)
        )
        if new_title is None:
            return
        full_title = (
            f"[{item.name_project}] - {new_title}"
            if item.name_project
            else new_title
        )
        await asyncio.to_thread(
            self._engine.update_work_item_title, item.id, full_title
        )
        self.notify(f"Renamed → {new_title}", timeout=2)
        self._fetch_items()

    @work
    async def action_new_task(self) -> None:
        current_timebox = next(
            (tb for tb in self._timeboxes if tb.is_current), None
        )
        data: NewTaskData | None = await self.push_screen_wait(
            CreateScreen(self._timeboxes, current_timebox)
        )
        if data is None:
            return
        item = await asyncio.to_thread(
            self._engine.create_work_item_helper,
            data.title,
            description=data.description,
            item_type=data.item_type,
        )
        if data.state != WorkItemState.NEW:
            await asyncio.to_thread(
                self._engine.update_work_item_state, item.id, data.state
            )
        if data.timebox is not None:
            await asyncio.to_thread(self._engine.set_timebox, item.id, data.timebox)
        self.notify(f"Created: {data.title}", timeout=2)
        self._fetch_items()

    @work
    async def action_pick_state(self) -> None:
        item = self._cursor_item()
        if item is None:
            return
        new_state: WorkItemState | None = await self.push_screen_wait(
            StatePickerScreen()
        )
        if new_state is None:
            return
        cursor_row = self.query_one(WorkItemTable).cursor_row
        await asyncio.to_thread(
            self._engine.update_work_item_state, item.id, new_state
        )
        if 0 <= cursor_row < len(self._items):
            self._items = (
                *self._items[:cursor_row],
                replace(self._items[cursor_row], state=new_state),
                *self._items[cursor_row + 1 :],
            )
        self._refresh_view(preserve_cursor=True)
        self.notify(f"State → {new_state.value}", timeout=2)

    async def action_timebox_next(self) -> None:
        await self._move_timebox(+1)

    async def action_timebox_prev(self) -> None:
        await self._move_timebox(-1)

    async def _move_timebox(self, direction: int) -> None:
        item = self._cursor_item()
        if item is None or not self._timeboxes:
            return
        current_number = (
            item.iteration_path.optional_number if item.iteration_path else None
        )
        if current_number is None:
            self.notify("Item has no timebox", severity="warning", timeout=3)
            return
        target = adjacent_timebox(self._timeboxes, current_number, direction)
        if target is None:
            self.notify("No timebox in that direction", severity="warning", timeout=3)
            return
        await asyncio.to_thread(self._engine.set_timebox, item.id, target)
        self.notify(f"TB → {target.path.optional_number}", timeout=2)
        self._fetch_items()

    async def action_show_branch(self) -> None:
        item = self._cursor_item()
        if item is None:
            return
        name = branch_name(item)
        copied = await asyncio.to_thread(copy_to_clipboard, name)
        suffix = " (copied)" if copied else ""
        self.notify(name + suffix, title="Branch name", timeout=5)
