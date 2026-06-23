from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Select

from azz.core.timebox import Iteration
from azz.core.work_item import WorkItemState
from azz.core.work_item.work_item_type import WorkItemType
from azz.tui.timebox_nav import adjacent_timebox


@dataclass(frozen=True)
class NewTaskData:
    title: str
    state: WorkItemState
    item_type: WorkItemType
    timebox: Iteration | None


class CreateScreen(ModalScreen[NewTaskData | None]):
    CSS = """
    CreateScreen { align: center middle; }
    #dialog {
        width: 72;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 1 2;
    }
    .row { height: auto; margin-top: 1; }
    .field { width: 1fr; height: auto; }
    #tb-value {
        height: 3;
        content-align: center middle;
        border: tall $background;
    }
    """

    BINDINGS: ClassVar = [
        Binding("escape", "dismiss_none", "Cancel"),
        Binding("ctrl+s", "submit_form", "Create"),
    ]

    _STATE_OPTIONS: ClassVar[tuple[tuple[str, WorkItemState], ...]] = (
        (WorkItemState.NEW.value, WorkItemState.NEW),
        (WorkItemState.ACTIVE.value, WorkItemState.ACTIVE),
        (WorkItemState.DESIGN.value, WorkItemState.DESIGN),
    )

    _TYPE_OPTIONS: ClassVar[tuple[tuple[str, WorkItemType], ...]] = (
        (WorkItemType.TASK.value, WorkItemType.TASK),
        (WorkItemType.USER_STORY.value, WorkItemType.USER_STORY),
        (WorkItemType.BUG.value, WorkItemType.BUG),
    )

    def __init__(
        self,
        timeboxes: tuple[Iteration, ...],
        current_timebox: Iteration | None,
    ) -> None:
        super().__init__()
        self._timeboxes = timeboxes
        self._selected_timebox = current_timebox

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("[bold]New Task[/bold]")
            yield Input(placeholder="Title — Enter to create", id="title-input")
            with Horizontal(classes="row"):
                with Vertical(classes="field"):
                    yield Label("State")
                    yield Select(
                        self._STATE_OPTIONS,
                        value=WorkItemState.NEW,
                        allow_blank=False,
                        id="state-select",
                    )
                with Vertical(classes="field"):
                    yield Label("Type")
                    yield Select(
                        self._TYPE_OPTIONS,
                        value=WorkItemType.TASK,
                        allow_blank=False,
                        id="type-select",
                    )
                with Vertical(classes="field"):
                    yield Label("Timebox  [dim]±[/dim]")
                    yield Label(self._tb_display(), id="tb-value")
            yield Label(
                "[dim]Enter: create · Tab: navigate · ±: timebox · Esc: cancel[/dim]",
                classes="row",
            )

    def on_mount(self) -> None:
        self.query_one("#title-input", Input).focus()

    def _tb_display(self) -> str:
        if self._selected_timebox is None:
            return "─"
        number = self._selected_timebox.path.optional_number
        return f"TB {number}" if number is not None else self._selected_timebox.name

    def on_key(self, event: Key) -> None:
        if self.focused is self.query_one("#title-input", Input):
            return
        if event.key == "plus":
            self._adjust_timebox(+1)
            event.prevent_default()
        elif event.key == "minus":
            self._adjust_timebox(-1)
            event.prevent_default()

    def _adjust_timebox(self, direction: int) -> None:
        if self._selected_timebox is None:
            return
        current_number = self._selected_timebox.path.optional_number
        if current_number is None:
            return
        target = adjacent_timebox(self._timeboxes, current_number, direction)
        if target is not None:
            self._selected_timebox = target
            self.query_one("#tb-value", Label).update(self._tb_display())

    @on(Input.Submitted)
    def on_title_submitted(self, event: Input.Submitted) -> None:
        self._submit(event.value)

    def action_submit_form(self) -> None:
        self._submit(self.query_one("#title-input", Input).value)

    def _submit(self, raw_title: str) -> None:
        title = raw_title.strip()
        if not title:
            return
        state_val = self.query_one("#state-select", Select).value
        type_val = self.query_one("#type-select", Select).value
        state = (
            state_val
            if isinstance(state_val, WorkItemState)
            else WorkItemState.NEW
        )
        item_type = (
            type_val
            if isinstance(type_val, WorkItemType)
            else WorkItemType.TASK
        )
        self.dismiss(NewTaskData(
            title=title,
            state=state,
            item_type=item_type,
            timebox=self._selected_timebox,
        ))

    def action_dismiss_none(self) -> None:
        self.dismiss(None)
