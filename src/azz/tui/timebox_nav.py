from __future__ import annotations

from collections.abc import Sequence

from azz.core.timebox import Iteration


def adjacent_timebox(
    timeboxes: Sequence[Iteration],
    current_number: int,
    direction: int,
) -> Iteration | None:
    sorted_timeboxes = sorted(
        timeboxes, key=lambda timebox: timebox.path.optional_number or 0
    )
    current_position = next(
        (
            position
            for position, timebox in enumerate(sorted_timeboxes)
            if timebox.path.optional_number == current_number
        ),
        None,
    )
    if current_position is None:
        return None
    new_position = current_position + direction
    if not (0 <= new_position < len(sorted_timeboxes)):
        return None
    return sorted_timeboxes[new_position]
