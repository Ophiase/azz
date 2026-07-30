from pathlib import Path


class CacheError(Exception):
    pass


class CorruptCacheEntry(CacheError):
    def __init__(self, path: Path, reason: str) -> None:
        super().__init__(f"{path}: {reason}")
        self.path = path
        self.reason = reason
