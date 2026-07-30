from dataclasses import dataclass

from .change import Change
from .change_type import ChangeType


@dataclass(frozen=True, slots=True)
class Changeset:
    changes: tuple[Change, ...]

    def of_type(self, change_type: ChangeType) -> tuple[Change, ...]:
        return tuple(
            change for change in self.changes if change.change_type is change_type
        )

    @property
    def applicable(self) -> tuple[Change, ...]:
        """Creations first, then updates — never NOOP or GONE."""
        return self.of_type(ChangeType.CREATE) + self.of_type(ChangeType.UPDATE)
