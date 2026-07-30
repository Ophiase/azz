from collections.abc import Mapping, Sequence
from logging import getLogger

from azz.core.engine import Engine
from azz.core.work_item import WorkItem

from .batch_reader import BatchWorkItemReader

logger = getLogger(__name__)


class RemoteResolver:
    """
    Turns work item ids into remote items with as few `az` calls as possible.

    One batched query covers every id in the management project. Ids it does
    not return are retried one at a time, because the batched query is scoped
    to a single project while `get_workitem` is not — so a genuinely missing
    id is only reported missing after both attempts fail.
    """

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def resolve(self, work_item_ids: Sequence[int]) -> Mapping[int, WorkItem]:
        wanted = tuple(dict.fromkeys(work_item_ids))
        if not wanted:
            return {}
        resolved = dict(self._batch(wanted))
        for work_item_id in wanted:
            if work_item_id in resolved:
                continue
            single = self._single(work_item_id)
            if single is not None:
                resolved[work_item_id] = single
        return resolved

    def _batch(self, work_item_ids: Sequence[int]) -> Mapping[int, WorkItem]:
        if not isinstance(self._engine, BatchWorkItemReader):
            return {}
        try:
            items = self._engine.get_work_items_by_id(work_item_ids)
        except (RuntimeError, ValueError) as error:
            logger.debug("batched lookup failed, falling back to one call per id: %s",
                         error)
            return {}
        return {item.id: item for item in items}

    def _single(self, work_item_id: int) -> WorkItem | None:
        try:
            return self._engine.get_workitem(work_item_id)
        except RuntimeError:
            logger.debug("work item %s not reachable on the remote", work_item_id)
            return None
