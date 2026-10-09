from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Final

from azz.core.runner import run_az_command_sync

from .azure_repository import AzureRepository
from .git_checkout import BranchName
from .pull_request_draft import PullRequestDraft, Reviewer

BRANCH_REF_PREFIX: Final = "refs/heads/"

type PullRequestId = int


@dataclass(frozen=True, slots=True)
class AzurePullRequests:
    repository: AzureRepository

    @staticmethod
    def signed_in_user() -> Reviewer:
        account = run_az_command_sync("account", "show", "-o", "json")
        return _as_mapping(account)["user"]["name"]

    def default_branch(self) -> BranchName:
        repository = self._az_in_project(
            "repos", "show", "--repository", self.repository.name
        )
        return _as_mapping(repository)["defaultBranch"].removeprefix(BRANCH_REF_PREFIX)

    def find_active(self, source_branch: BranchName) -> PullRequestId | None:
        listing = self._az_in_project(
            "repos", "pr", "list",
            "--repository", self.repository.name,
            "--source-branch", source_branch,
            "--status", "active",
        )
        return next((item["pullRequestId"] for item in _as_sequence(listing)), None)

    def create(self, draft: PullRequestDraft) -> PullRequestId:
        created = self._az_in_project(
            "repos", "pr", "create",
            "--repository", self.repository.name,
            "--source-branch", draft.source_branch,
            "--target-branch", draft.target_branch,
            "--title", draft.title,
            "--draft", str(draft.is_draft).lower(),
            *_optional("--description", draft.description),
            *_many("--work-items", map(str, draft.work_item_ids)),
            *_many("--reviewers", draft.reviewers),
        )
        return _as_mapping(created)["pullRequestId"]

    def update(self, pull_request_id: PullRequestId, draft: PullRequestDraft) -> None:
        """Rewrite the title and description; links and reviewers are only added."""
        identifier = ("--id", str(pull_request_id))
        self._az(
            "repos", "pr", "update", *identifier,
            "--title", draft.title,
            *_optional("--description", draft.description),
        )
        if draft.work_item_ids:
            self._az(
                "repos", "pr", "work-item", "add", *identifier,
                *_many("--work-items", map(str, draft.work_item_ids)),
            )
        if draft.reviewers:
            self._az(
                "repos", "pr", "reviewer", "add", *identifier,
                *_many("--reviewers", draft.reviewers),
            )

    def _az_in_project(self, *arguments: str) -> list | dict:
        return self._az(*arguments, "--project", self.repository.project)

    def _az(self, *arguments: str) -> list | dict:
        return run_az_command_sync(
            *arguments,
            "--organization", self.repository.organization_url,
            "--detect", "false",
            "-o", "json",
        )


def _optional(flag: str, value: str) -> tuple[str, ...]:
    return (flag, value) if value else ()


def _many(flag: str, values: Iterable[str]) -> tuple[str, ...]:
    collected = tuple(values)
    return (flag, *collected) if collected else ()


def _as_mapping(result: Any) -> dict:
    if not isinstance(result, dict):
        raise RuntimeError(f"Unexpected result format from az command: {result}")
    return result


def _as_sequence(result: Any) -> list:
    if not isinstance(result, list):
        raise RuntimeError(f"Unexpected result format from az command: {result}")
    return result
