from pathlib import Path


class PlanError(Exception):
    pass


class IntentFileError(PlanError):
    def __init__(self, path: Path, reason: str) -> None:
        super().__init__(f"{path}: {reason}")
        self.path = path
        self.reason = reason
