from datetime import datetime
from typing import Any, Self

from pydantic.dataclasses import dataclass

from .iteration_path import IterationPath


@dataclass(frozen=True, slots=True)
class Iteration:
    id: int
    name: str
    path: IterationPath
    start_date: datetime | None = None
    finish_date: datetime | None = None

    @property
    def number(self) -> int:
        return self.path.number

    @classmethod
    def from_fields(cls, data: dict[str, Any], normalize_path: bool = True) -> Self:
        attributes = data.get("attributes", {})

        start_date = attributes.get("startDate")
        finish_date = attributes.get("finishDate")

        return cls(
            id=data["id"],
            name=data["name"],
            path=IterationPath.create_and_normalize(data["path"])
            if normalize_path
            else IterationPath(data["path"]),
            start_date=datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            if start_date
            else None,
            finish_date=datetime.fromisoformat(finish_date.replace("Z", "+00:00"))
            if finish_date
            else None,
        )

    @property
    def is_current(self) -> bool:
        if self.start_date is None or self.finish_date is None:
            return False

        now = datetime.now(tz=self.start_date.tzinfo) if self.start_date else None
        if now is None:
            return False

        return (
            self.start_date is not None
            and self.finish_date is not None
            and self.start_date <= now <= self.finish_date
        )

    def render(self) -> str:
        return f"{self.name} ({self.start_date:%Y-%m-%d} - {self.finish_date:%Y-%m-%d})"

    def render_all(self) -> str:
        return f"{self.render()} - {self.id} - '[green]({self.path.value})[/green]'"
