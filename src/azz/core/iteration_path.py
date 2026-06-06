from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True, slots=True)
class IterationPath:
    value: str
    normalized: bool = False

    @property
    def number(self) -> int:
        try:
            last_word = self.value.split()[-1]
            return int(last_word)
        except (IndexError, ValueError) as e:
            raise ValueError(
                f"Cannot extract number from iteration path: {self.value}"
            ) from e

    @property
    def optional_number(self) -> int | None:
        try:
            return self.number
        except ValueError:
            return None

    def normalize(self) -> Self:
        if self.normalized:
            return self
        return self.create_and_normalize(self.value)

    @classmethod
    def create_and_normalize(cls, value: str) -> Self:
        parts = [p for p in value.split("\\") if p]

        if len(parts) >= 3 and parts[1].lower() == "iteration":
            parts.pop(1)

        return cls(
            value="\\".join(parts),
            normalized=True,
        )

    @classmethod
    def empty(cls) -> Self:
        return cls(value="")
