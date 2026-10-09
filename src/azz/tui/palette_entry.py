from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final, Self

from textual.binding import Binding, BindingType

KEY_LABELS: Final = {
    "question_mark": "?",
    "plus": "+",
    "minus": "-",
    "escape": "Esc",
    "up": "↑",
    "down": "↓",
}
HIDDEN_ACTIONS: Final = frozenset({"escape_mode"})


@dataclass(frozen=True, slots=True)
class PaletteEntry:
    """One action, with every key bound to it."""

    name: str
    keys: tuple[str, ...]
    action: str

    @property
    def help(self) -> str:
        return " / ".join(KEY_LABELS.get(key, key) for key in self.keys)

    @classmethod
    def from_bindings(cls, bindings: Sequence[BindingType]) -> tuple[Self, ...]:
        """One entry per action, so `j` and `down` appear as a single command.

        Descriptions carry footer hints like `[a]Closed`; the palette shows the
        name alone and puts the keys beside it.
        """
        grouped: dict[str, list[Binding]] = {}
        for binding in Binding.make_bindings(bindings):
            if binding.action not in HIDDEN_ACTIONS:
                grouped.setdefault(binding.action, []).append(binding)
        return tuple(
            cls(
                name=_readable(bound),
                keys=tuple(binding.key for binding in bound),
                action=action,
            )
            for action, bound in grouped.items()
        )


def _readable(bound: Sequence[Binding]) -> str:
    described = next(
        (binding.description for binding in bound if binding.description), ""
    )
    return _without_footer_hint(described) or bound[0].action.replace("_", " ")


def _without_footer_hint(description: str) -> str:
    """`[a]Closed` is a footer label; the palette wants `Closed`."""
    if description.startswith("[") and "]" in description:
        return description.split("]", 1)[1].strip()
    return description.strip()
