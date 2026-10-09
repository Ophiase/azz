import subprocess  # noqa: S404
from dataclasses import dataclass
from pathlib import Path
from typing import Final

type BranchName = str
type RemoteName = str

DEFAULT_REMOTE: Final = "origin"


@dataclass(frozen=True, slots=True)
class GitCheckout:
    """A working tree — the main checkout or any of its worktrees."""

    directory: Path = Path()

    @property
    def current_branch(self) -> BranchName:
        branch = self._git("branch", "--show-current")
        if not branch:
            raise RuntimeError("HEAD is detached: name the branch explicitly")
        return branch

    def remote_of(self, branch: BranchName) -> RemoteName:
        """The remote the branch tracks, or `origin` when it tracks none yet."""
        configured = self._git(
            "config", "--get", f"branch.{branch}.remote", check=False
        )
        return configured or DEFAULT_REMOTE

    def remote_url(self, remote: RemoteName) -> str:
        return self._git("remote", "get-url", remote)

    def commit_subjects(
        self, remote: RemoteName, target: BranchName, branch: BranchName
    ) -> tuple[str, ...]:
        """Subjects of the commits `branch` adds on top of the remote `target`."""
        listing = self._git(
            "log", "--format=%s", "--reverse", f"{remote}/{target}..{branch}"
        )
        return tuple(listing.splitlines())

    def fetch(self, remote: RemoteName, branch: BranchName) -> None:
        self._git("fetch", "--quiet", remote, branch)

    def push(self, remote: RemoteName, branch: BranchName) -> None:
        self._git("push", "--quiet", "--set-upstream", remote, branch)

    def _git(self, *arguments: str, check: bool = True) -> str:
        completed = subprocess.run(  # noqa: S603
            ("git", "-C", str(self.directory), *arguments),  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
        )
        if check and completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or f"git {arguments[0]} failed")
        return completed.stdout.strip()
