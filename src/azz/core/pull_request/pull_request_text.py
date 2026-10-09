from collections.abc import Sequence
from dataclasses import dataclass
from typing import Self

from azz.core.work_item import WorkItem

from .git_checkout import BranchName


@dataclass(frozen=True, slots=True)
class PullRequestText:
    title: str
    description: str

    @classmethod
    def fallback(
        cls,
        branch: BranchName,
        work_item: WorkItem | None,
        commit_subjects: Sequence[str],
    ) -> Self:
        """Title from the work item, else the first commit, else the branch;
        the description lists the commits."""
        if work_item is not None:
            title = work_item.stripped_name
        else:
            title = commit_subjects[0] if commit_subjects else branch
        description = "\n".join(f"- {subject}" for subject in commit_subjects)
        return cls(title, description)
