from datetime import datetime
from importlib.resources import files
from typing import Final, Self

from pydantic import BaseModel

from azz.cache import CacheStore, ItemPayload

from .item import DemoItem
from .timebox import DemoTimebox

BOARD_FILE_NAME: Final = "board.json"


class DemoBoard(BaseModel):
    """
    The fictional board shipped with the package, and how to lay it down.

    Every name here is invented. It exists so the TUI can be recorded without
    putting a single real work item on screen.
    """

    owner: str
    project: str
    timeboxes: tuple[DemoTimebox, ...]
    items: tuple[DemoItem, ...]

    @classmethod
    def load(cls) -> Self:
        resource = files(__package__).joinpath(BOARD_FILE_NAME)
        return cls.model_validate_json(resource.read_text(encoding="utf-8"))

    def materialize(self, store: CacheStore, reference: datetime) -> None:
        store.write_timeboxes([
            timebox.to_fields(self.project, reference) for timebox in self.timeboxes
        ])
        store.write_items([
            self._payload(item, reference) for item in self.items
        ])

    def _payload(self, item: DemoItem, reference: datetime) -> ItemPayload:
        return item.to_payload(
            self.project,
            self.owner,
            self._timebox_path(item.timebox_number),
            reference,
        )

    def _timebox_path(self, timebox_number: int | None) -> str | None:
        timebox = next(
            (
                candidate
                for candidate in self.timeboxes
                if candidate.number == timebox_number
            ),
            None,
        )
        return timebox.path(self.project) if timebox else None
