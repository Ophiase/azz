import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Final

from azz.core.timebox import Iteration
from azz.core.work_item import WorkItem

from .errors import CorruptCacheEntry
from .payload import ItemPayload

ITEMS_DIRECTORY_NAME: Final = "items"
TIMEBOXES_FILE_NAME: Final = "timeboxes.json"
FIRST_LOCAL_ITEM_ID: Final = 1


class CacheStore:
    """
    Reads and writes our knowledge of the remote, one JSON file per item.

    Layout-agnostic on purpose: it is handed a directory and never asks where
    `.azz` is. Writes are atomic, so an interrupted fetch cannot leave a
    half-written entry behind.
    """

    def __init__(self, cache_root: Path) -> None:
        self._root = cache_root

    @property
    def root(self) -> Path:
        return self._root

    @property
    def exists(self) -> bool:
        return self._items_directory.is_dir()

    @property
    def _items_directory(self) -> Path:
        return self._root / ITEMS_DIRECTORY_NAME

    def _item_path(self, work_item_id: int) -> Path:
        return self._items_directory / f"{work_item_id}.json"

    def write_item(self, payload: ItemPayload) -> None:
        _write_json(self._item_path(payload.item_id), payload.data)

    def write_items(self, payloads: Sequence[ItemPayload]) -> None:
        for payload in payloads:
            self.write_item(payload)

    def read_payload(self, work_item_id: int) -> ItemPayload | None:
        path = self._item_path(work_item_id)
        if not path.is_file():
            return None
        return ItemPayload(_read_json(path))

    def read_item(self, work_item_id: int) -> WorkItem | None:
        payload = self.read_payload(work_item_id)
        return payload.to_work_item() if payload else None

    def read_all_payloads(self) -> tuple[ItemPayload, ...]:
        if not self.exists:
            return ()
        paths = sorted(self._items_directory.glob("*.json"), key=_numeric_stem)
        return tuple(ItemPayload(_read_json(path)) for path in paths)

    def read_all_items(self) -> tuple[WorkItem, ...]:
        return tuple(payload.to_work_item() for payload in self.read_all_payloads())

    def item_ids(self) -> frozenset[int]:
        if not self.exists:
            return frozenset()
        return frozenset(
            int(path.stem)
            for path in self._items_directory.glob("*.json")
            if path.stem.lstrip("-").isdigit()
        )

    def delete_item(self, work_item_id: int) -> bool:
        path = self._item_path(work_item_id)
        if not path.is_file():
            return False
        path.unlink()
        return True

    def next_item_id(self) -> int:
        known = self.item_ids()
        return max(known) + 1 if known else FIRST_LOCAL_ITEM_ID

    def write_timeboxes(self, payloads: Sequence[Mapping[str, Any]]) -> None:
        _write_json(self._root / TIMEBOXES_FILE_NAME, list(payloads))

    def read_timeboxes(self) -> tuple[Iteration, ...]:
        path = self._root / TIMEBOXES_FILE_NAME
        if not path.is_file():
            return ()
        document = _read_json(path)
        if not isinstance(document, list):
            raise CorruptCacheEntry(path, "expected a list of iterations")
        return tuple(Iteration.from_fields(entry) for entry in document)


def _numeric_stem(path: Path) -> tuple[int, str]:
    return (int(path.stem), path.stem) if path.stem.isdigit() else (0, path.stem)


def _write_json(path: Path, document: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.writing")
    temporary.write_text(json.dumps(document, indent=2) + "\n")
    temporary.replace(path)


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise CorruptCacheEntry(path, f"invalid JSON: {error}") from error
