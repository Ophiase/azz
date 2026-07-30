from collections.abc import Sequence
from datetime import timedelta
from typing import Final

from rich.markup import escape

from .models import PullOutcome, PullStatus, SyncEntry, SyncReport, SyncState
from .renderer import display_path

LABEL_WIDTH: Final = 10
DIFF_INDENT: Final = " " * (LABEL_WIDTH + 4)
DEGRADED_MARK: Final = "[magenta]?[/magenta]"
DEGRADED_NOTICE: Final = (
    "[magenta]? no merge base for {count} file(s) — the verdict is the two-way "
    "one. Run [bold]azz plan fetch[/bold] then [bold]azz plan pull[/bold]."
    "[/magenta]"
)
EMPTY_CACHE_NOTICE: Final = (
    "[yellow]The cache is empty, so nothing can be compared offline. "
    "Run [bold]azz plan fetch[/bold] first.[/yellow]"
)
NEVER_FETCHED_NOTICE: Final = "[grey50]cache never stamped[/grey50]"
STALE_NOTICE: Final = "[yellow]cache is {age} old — run azz plan fetch[/yellow]"
FRESH_NOTICE: Final = "[grey50]cache fetched {age} ago[/grey50]"


def render_sync_report(report: SyncReport) -> str:
    lines = [render_sync_entry(entry) for entry in report.entries]
    lines.extend(_incoming_line(report))
    return "\n".join(line for line in lines if line)


def render_sync_entry(entry: SyncEntry) -> str:
    label = escape(f"[{entry.state.label}]".ljust(LABEL_WIDTH))
    mark = DEGRADED_MARK if entry.degraded else " "
    lines = [
        f"[{entry.state.style}]{label}[/{entry.state.style}]{mark}"
        f"{escape(display_path(entry.local_item.path))}"
        f"{_identifier(entry)} {entry.state.description}"
    ]
    lines.extend(f"{DIFF_INDENT}{diff.render()}" for diff in entry.field_diffs)
    return "\n".join(lines)


def render_sync_summary(report: SyncReport) -> str:
    counts = ", ".join(
        f"{len(report.of_state(state))} {state.label.lower()}" for state in SyncState
    )
    incoming = f", {len(report.incoming)} incoming" if report.incoming else ""
    return f"[bold]{counts}{incoming}[/bold]"


def render_sync_notices(report: SyncReport) -> str:
    if not report.has_cache:
        return EMPTY_CACHE_NOTICE
    degraded = report.degraded
    return DEGRADED_NOTICE.format(count=len(degraded)) if degraded else ""


def render_cache_age(age: timedelta | None, stale: bool) -> str:
    if age is None:
        return NEVER_FETCHED_NOTICE
    template = STALE_NOTICE if stale else FRESH_NOTICE
    return template.format(age=_humanize(age))


def render_pull_outcome(outcome: PullOutcome) -> str:
    status = outcome.status
    label = escape(f"[{status.label}]".ljust(LABEL_WIDTH))
    identifier = f" [grey50]#{outcome.item_id}[/grey50]" if outcome.item_id else ""
    reason = f" [yellow]({escape(outcome.reason)})[/yellow]" if outcome.reason else ""
    return (
        f"[{status.style}]{label}[/{status.style}] "
        f"{escape(display_path(outcome.path))}{identifier}{reason}"
    )


def render_pull_summary(outcomes: Sequence[PullOutcome]) -> str:
    counts = ", ".join(
        f"{sum(1 for outcome in outcomes if outcome.status is status)} "
        f"{status.label.lower()}"
        for status in PullStatus
    )
    return f"[bold]{counts}[/bold]"


def _incoming_line(report: SyncReport) -> tuple[str, ...]:
    if not report.incoming:
        return ()
    identifiers = ", ".join(f"#{item.id}" for item in report.incoming)
    return (
        f"[cyan]{escape('[INCOMING]'.ljust(LABEL_WIDTH))}[/cyan] "
        f"{len(report.incoming)} cached item(s) with no local file: "
        f"{identifiers}",
    )


def _identifier(entry: SyncEntry) -> str:
    item_id = entry.local_item.item_id
    return f" (#{item_id})" if item_id is not None else ""


def _humanize(age: timedelta) -> str:
    hours = int(age.total_seconds() // 3600)
    if hours < 1:
        return f"{max(int(age.total_seconds() // 60), 1)} minutes"
    if hours < 48:
        return f"{hours} hours"
    return f"{hours // 24} days"
