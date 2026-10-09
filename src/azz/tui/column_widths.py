from collections.abc import Sequence

from rich.cells import cell_len
from rich.text import Text

type Cell = str | Text


def column_widths(
    labels: Sequence[str], rows: Sequence[Sequence[Cell]]
) -> tuple[int, ...]:
    """Each column as wide as its widest label or cell, in terminal cells.

    Known before the first paint, unlike `DataTable`'s auto widths, which are
    settled on idle and leave rows painted earlier cached at the old width.
    """
    columns = zip(labels, *rows, strict=True)
    return tuple(max(_width(cell) for cell in column) for column in columns)


def _width(cell: Cell) -> int:
    return cell.cell_len if isinstance(cell, Text) else cell_len(cell)
