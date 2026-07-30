from datetime import datetime, timedelta
from typing import Any, Final

from pydantic import BaseModel

SPRINT_LABEL: Final = "Sprint"
IDENTIFIER_BASE: Final = 5000


class DemoTimebox(BaseModel):
    """
    One fictional sprint, dated relative to whenever the demo is run.

    Offsets rather than absolute dates: a fixture with hardcoded dates would
    stop having a current sprint a month after it was written, and the whole
    point of the demo board is that it always looks like a live one.
    """

    number: int
    start_offset_days: int
    finish_offset_days: int

    @property
    def name(self) -> str:
        return f"{SPRINT_LABEL} {self.number}"

    @property
    def identifier(self) -> int:
        return IDENTIFIER_BASE + self.number

    def path(self, project: str) -> str:
        return f"{project}\\{self.name}"

    def to_fields(self, project: str, reference: datetime) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "name": self.name,
            "path": self.path(project),
            "attributes": {
                "startDate": self._moment(reference, self.start_offset_days),
                "finishDate": self._moment(reference, self.finish_offset_days),
            },
        }

    @staticmethod
    def _moment(reference: datetime, offset_days: int) -> str:
        return (reference + timedelta(days=offset_days)).isoformat()
