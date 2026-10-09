from dataclasses import dataclass

from .git_checkout import BranchName

type Reviewer = str


@dataclass(frozen=True, slots=True)
class PullRequestDraft:
    source_branch: BranchName
    target_branch: BranchName
    title: str
    description: str
    work_item_ids: tuple[int, ...]
    reviewers: tuple[Reviewer, ...]
    is_draft: bool = False
