import os
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Final, Self

from azz.cache import CacheStore
from azz.cache.backend import CacheBackend
from azz.core.engine_config import EngineConfig

from .board import DemoBoard

DEMO_DIRECTORY_VARIABLE: Final = "AZZ_DEMO_DIR"
DEMO_ORGANIZATION_URL: Final = "https://dev.azure.com/tidepool-demo"
DEMO_REPOSITORY: Final = "tidepool"
TEMPORARY_PREFIX: Final = "azz-demo-"


class DemoSession:
    """
    A self-contained fake board: packaged fixture in, `CacheBackend` out.

    Ephemeral by default. The fixture is materialized into a throwaway
    directory, so every recording starts from the same board and the renames
    and state changes made on camera vanish with the process. Set
    `AZZ_DEMO_DIR` to keep them across runs instead.
    """

    def __init__(
        self,
        board: DemoBoard,
        root: Path,
        temporary: TemporaryDirectory[str] | None = None,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._board = board
        self._temporary = temporary
        self._store = CacheStore(root)
        self._now = now
        if not self._store.exists:
            board.materialize(self._store, now())

    @classmethod
    def start(cls) -> Self:
        board = DemoBoard.load()
        configured = os.getenv(DEMO_DIRECTORY_VARIABLE)
        if configured:
            return cls(board, Path(configured).expanduser())
        temporary = TemporaryDirectory(prefix=TEMPORARY_PREFIX)
        return cls(board, Path(temporary.name), temporary)

    @property
    def root(self) -> Path:
        return self._store.root

    @property
    def is_ephemeral(self) -> bool:
        return self._temporary is not None

    @property
    def notice(self) -> str:
        """What the TUI and any banner should say about this board."""
        origin = (
            "changes discarded on exit"
            if self.is_ephemeral
            else f"stored in {self.root}"
        )
        return f"DEMO DATA - fictional board ({origin})"

    @property
    def config(self) -> EngineConfig:
        return EngineConfig(
            org_url=DEMO_ORGANIZATION_URL,
            default_project=self._board.project,
            management_project=self._board.project,
            default_repo=DEMO_REPOSITORY,
            editor=os.getenv("EDITOR", "nvim"),
            prepend_project_name=False,
        )

    @property
    def backend(self) -> CacheBackend:
        return CacheBackend(
            self._store, self.config, owner=self._board.owner, now=self._now
        )
