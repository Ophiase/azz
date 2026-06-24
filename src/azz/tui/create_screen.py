from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Select

from azz.core.timebox import Iteration
from azz.core.work_item import WorkItemState
from azz.core.work_item.work_item_type import WorkItemType


@dataclass(frozen=True)
class NewTaskData:
    title: str
    state: WorkItemState
    item_type: WorkItemType
    timebox: Iteration | None
    description: str | None


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
        (WorkItemType.EPIC.value, WorkItemType.EPIC),
        (WorkItemType.FEATURE.value, WorkItemType.FEATURE),
        (WorkItemType.ISSUE.value, WorkItemType.ISSUE),
    )

    def __init__(
        self,
        timeboxes: tuple[Iteration, ...],
        current_timebox: Iteration | None,
    ) -> None:
        super().__init__()
        self._timeboxes = timeboxes
        self._current_timebox = current_timebox

    def _tb_options(self) -> tuple[tuple[str, Iteration], ...]:
        return tuple(
            (
                f"TB {tb.path.optional_number}"
                if tb.path.optional_number is not None
                else tb.name,
                tb,
            )
            for tb in self._timeboxes
        )

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
                    yield Label("Timebox")
                    yield Select(
                        self._tb_options(),
                        value=self._current_timebox,
                        allow_blank=True,
                        id="tb-select",
                    )
            yield Label("Description  [dim](optional)[/dim]", classes="row")
            yield Input(placeholder="Short description", id="desc-input")
            yield Label(
                "[dim]Enter/Ctrl+S: create · Tab: navigate · Esc: cancel[/dim]",
                classes="row",
            )

    def on_mount(self) -> None:
        self.query_one("#title-input", Input).focus()

    @on(Input.Submitted)
    def on_input_submitted(self) -> None:
        self._submit(self.query_one("#title-input", Input).value)

    def action_submit_form(self) -> None:
        self._submit(self.query_one("#title-input", Input).value)

    def _submit(self, raw_title: str) -> None:
        title = raw_title.strip()
        if not title:
            return
        state_val = self.query_one("#state-select", Select).value
        type_val = self.query_one("#type-select", Select).value
        tb_val = self.query_one("#tb-select", Select).value
        desc_raw = self.query_one("#desc-input", Input).value.strip()
        state = (
            state_val if isinstance(state_val, WorkItemState) else WorkItemState.NEW
        )
        item_type = (
            type_val if isinstance(type_val, WorkItemType) else WorkItemType.TASK
        )
        timebox = tb_val if isinstance(tb_val, Iteration) else None
        self.dismiss(NewTaskData(
            title=title,
            state=state,
            item_type=item_type,
            timebox=timebox,
            description=desc_raw or None,
        ))

    def action_dismiss_none(self) -> None:
        self.dismiss(None)
