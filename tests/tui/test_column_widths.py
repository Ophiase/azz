"""Column widths are known before the first paint, so a row painted early is
never cached at a narrower width than its widest cell."""

from rich.text import Text

from azz.tui.column_widths import column_widths


def test_a_column_fits_its_widest_label_or_cell() -> None:
    rows = (
        ("08/10", Text("N"), "a long work item title"),
        ("30/09", Text("A"), "short"),
    )
    assert column_widths(("Date ↓", "S", "Name"), rows) == (6, 1, 22)


def test_without_rows_a_column_fits_its_label() -> None:
    assert column_widths(("", "ID"), ()) == (0, 2)
