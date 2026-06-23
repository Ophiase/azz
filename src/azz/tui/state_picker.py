from typing import ClassVar

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, ListItem, ListView

from azz.core.work_item import WorkItemState


class StatePickerScreen(ModalScreen[WorkItemState | None]):
    CSS = """
    StatePickerScreen { align: center middle; }
    #dialog {
        width: 30;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 1;
    }
    """

    BINDINGS: ClassVar = [Binding("escape", "dismiss_none", "Cancel")]

    _STATES: ClassVar[tuple[WorkItemState, ...]] = (
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
                *[
                    ListItem(Label(state.value), id=f"s-{state.value}")
                    for state in self._STATES
                ]
            )

    @on(ListView.Selected)
    def on_selected(self, event: ListView.Selected) -> None:
        raw_id = event.item.id or ""
        self.dismiss(WorkItemState.from_str(raw_id.removeprefix("s-")))

    def action_dismiss_none(self) -> None:
        self.dismiss(None)
