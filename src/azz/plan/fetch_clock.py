from datetime import UTC, datetime, timedelta
from logging import getLogger
from pathlib import Path
from typing import Final

STAMP_FILE_NAME: Final = "fetched-at"
STALE_AFTER: Final = timedelta(hours=12)

logger = getLogger(__name__)


class FetchClock:
    """
    When the cache last saw the remote.

    Separating `fetch` from `pull` means the cache can go quietly stale, so
    `azz plan status` reports its age the way `git status` reports being behind.
    """

    def __init__(self, cache_root: Path) -> None:
        self._path = cache_root / STAMP_FILE_NAME

    def stamp(self, moment: datetime | None = None) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text((moment or datetime.now(UTC)).isoformat() + "\n")

    @property
    def last_fetch(self) -> datetime | None:
        if not self._path.is_file():
            return None
        try:
            return datetime.fromisoformat(self._path.read_text().strip())
        except (OSError, ValueError) as error:
            logger.debug("unreadable fetch stamp at %s: %s", self._path, error)
            return None

    @property
    def age(self) -> timedelta | None:
        recorded = self.last_fetch
        if recorded is None:
            return None
        return datetime.now(recorded.tzinfo or UTC) - recorded

    @property
    def is_stale(self) -> bool:
        age = self.age
        return age is not None and age > STALE_AFTER
