from typing import ClassVar, Final

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, ListItem, ListView

from azz.core.work_item.priority import Priority
from azz.tui.priority_threshold import PriorityThreshold

ALL_ITEMS_ID: Final = "p-all"
_CHOICES: Final[tuple[tuple[str, PriorityThreshold], ...]] = (
    *((f"p-{int(level)}", PriorityThreshold(level)) for level in Priority),
    (ALL_ITEMS_ID, PriorityThreshold()),
)


class PriorityPickerScreen(ModalScreen[PriorityThreshold | None]):
    """Choose the least urgent priority still shown; Esc keeps the current one."""

    CSS = """
    PriorityPickerScreen { align: center middle; }
    #dialog {
        width: 34;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 1;
    }
    """

    BINDINGS: ClassVar = [
        Binding("escape", "dismiss_none", "Cancel"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("[bold]Show priority[/bold]")
            yield ListView(
                *(
                    ListItem(Label(_describe(threshold)), id=choice_id)
                    for choice_id, threshold in _CHOICES
                )
            )

    def action_cursor_down(self) -> None:
        self.query_one(ListView).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(ListView).action_cursor_up()

    @on(ListView.Selected)
    def on_selected(self, event: ListView.Selected) -> None:
        chosen = dict(_CHOICES).get(event.item.id or "")
        if chosen is not None:
            self.dismiss(chosen)

    def action_dismiss_none(self) -> None:
        self.dismiss(None)


def _describe(threshold: PriorityThreshold) -> str:
    if threshold.ceiling is None:
        return "all items"
    return f"{threshold.label}  {threshold.ceiling.name.lower()} and above"
