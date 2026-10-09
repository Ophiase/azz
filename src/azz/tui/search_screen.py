from __future__ import annotations

from typing import ClassVar, Final

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, OptionList
from textual.widgets.option_list import Option

from azz.core.work_item.work_item import WorkItem
from azz.tui.item_search import ItemSearch, search_label

MAX_RESULTS: Final = 50


class SearchScreen(ModalScreen[int | None]):
    """Type to fuzzy-search ids and titles; Enter returns the highlighted id."""

    CSS = """
    SearchScreen { align: center middle; }
    #dialog {
        width: 90;
        height: auto;
        max-height: 80%;
        border: solid $primary;
        background: $surface;
        padding: 1 2;
    }
    #search-results { height: auto; max-height: 20; }
    """

    BINDINGS: ClassVar = [
        Binding("escape", "dismiss_none", "Cancel"),
        Binding("down", "move_highlight(1)", "Down", show=False),
        Binding("up", "move_highlight(-1)", "Up", show=False),
    ]

    def __init__(self, items: tuple[WorkItem, ...]) -> None:
        super().__init__()
        self._search = ItemSearch(items)

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("[bold]Search[/bold] [dim]id or title · Enter: go[/dim]")
            yield Input(placeholder="/", id="search-input")
            yield OptionList(id="search-results")

    def on_mount(self) -> None:
        self.query_one(Input).focus()
        self._show("")

    @on(Input.Changed)
    def on_changed(self, event: Input.Changed) -> None:
        self._show(event.value)

    @on(Input.Submitted)
    def on_submitted(self) -> None:
        results = self.query_one(OptionList)
        if results.highlighted is None:
            return
        self._choose(results.get_option_at_index(results.highlighted))

    @on(OptionList.OptionSelected)
    def on_option_selected(self, event: OptionList.OptionSelected) -> None:
        self._choose(event.option)

    def action_move_highlight(self, step: int) -> None:
        results = self.query_one(OptionList)
        if results.option_count == 0:
            return
        current = results.highlighted or 0
        results.highlighted = max(0, min(current + step, results.option_count - 1))

    def action_dismiss_none(self) -> None:
        self.dismiss(None)

    def _choose(self, option: Option) -> None:
        if option.id is not None:
            self.dismiss(int(option.id))

    def _show(self, query: str) -> None:
        results = self.query_one(OptionList)
        results.clear_options()
        matches = self._search.matches(query)[:MAX_RESULTS]
        results.add_options(
            Option(Text(search_label(item)), id=str(item.id)) for item in matches
        )
        if matches:
            results.highlighted = 0
