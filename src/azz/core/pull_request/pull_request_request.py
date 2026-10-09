from dataclasses import dataclass

from .git_checkout import BranchName
from .pull_request_draft import Reviewer


@dataclass(frozen=True, slots=True)
class PullRequestRequest:
    """What the developer asked for; anything left `None` or empty is inferred."""

    branch: BranchName | None = None
    target_branch: BranchName | None = None
    title: str | None = None
    description: str | None = None
    extra_work_item_ids: tuple[int, ...] = ()
    reviewers: tuple[Reviewer, ...] = ()
    is_draft: bool = False
