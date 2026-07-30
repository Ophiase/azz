from datetime import UTC, datetime

from azz.core.work_item import WorkItem

from .models import LocalItem


def remote_is_ahead(local_item: LocalItem, remote_item: WorkItem) -> bool:
    """
    Whether the remote changed after the timestamp recorded locally.

    This is what separates "someone edited the remote since my last fetch"
    from "I edited this file locally" — both otherwise look like drift.
    """
    recorded = local_item.remote_changed_date
    if recorded is None or remote_item.changed_date is None:
        return False
    return _as_utc(remote_item.changed_date) > _as_utc(recorded)


def _as_utc(moment: datetime) -> datetime:
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)
