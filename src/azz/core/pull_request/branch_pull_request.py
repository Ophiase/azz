from dataclasses import dataclass
from typing import Protocol, Self

from azz.core.branch import work_item_id_from_branch
from azz.core.work_item import WorkItem

from .azure_pull_requests import AzurePullRequests, PullRequestId
from .azure_repository import AzureRepository
from .git_checkout import BranchName, GitCheckout, RemoteName
from .pull_request_draft import PullRequestDraft
from .pull_request_request import PullRequestRequest
from .pull_request_text import PullRequestText


class WorkItemSource(Protocol):
    def get_workitem(self, work_item_id: int) -> WorkItem: ...


@dataclass(frozen=True, slots=True)
class PublishedPullRequest:
    pull_request_id: PullRequestId
    url: str
    is_new: bool


@dataclass(frozen=True, slots=True)
class BranchPullRequest:
    """The pull request of one branch, in the repository its remote points at."""

    checkout: GitCheckout
    branch: BranchName
    remote: RemoteName
    repository: AzureRepository

    @classmethod
    def resolve(cls, checkout: GitCheckout, branch: BranchName | None) -> Self:
        branch = branch or checkout.current_branch
        remote = checkout.remote_of(branch)
        repository = AzureRepository.from_remote_url(checkout.remote_url(remote))
        return cls(checkout, branch, remote, repository)

    @property
    def pull_requests(self) -> AzurePullRequests:
        return AzurePullRequests(self.repository)

    def compose(
        self, request: PullRequestRequest, work_items: WorkItemSource
    ) -> PullRequestDraft:
        target = request.target_branch or self.pull_requests.default_branch()
        work_item_ids = self._work_item_ids(request)
        text = self._text(request, target, work_items, work_item_ids)
        return PullRequestDraft(
            source_branch=self.branch,
            target_branch=target,
            title=text.title,
            description=text.description,
            work_item_ids=work_item_ids,
            reviewers=request.reviewers or (AzurePullRequests.signed_in_user(),),
            is_draft=request.is_draft,
        )

    def publish(self, draft: PullRequestDraft) -> PublishedPullRequest:
        """Push the branch, then update its active pull request or open one."""
        self.checkout.push(self.remote, self.branch)
        existing = self.pull_requests.find_active(self.branch)
        if existing is not None:
            self.pull_requests.update(existing, draft)
        pull_request_id = existing or self.pull_requests.create(draft)
        return PublishedPullRequest(
            pull_request_id,
            self.repository.pull_request_url(pull_request_id),
            is_new=existing is None,
        )

    def _work_item_ids(self, request: PullRequestRequest) -> tuple[int, ...]:
        from_branch = work_item_id_from_branch(self.branch)
        ids = (from_branch, *request.extra_work_item_ids)
        return tuple(dict.fromkeys(item for item in ids if item is not None))

    def _text(
        self,
        request: PullRequestRequest,
        target: BranchName,
        work_items: WorkItemSource,
        work_item_ids: tuple[int, ...],
    ) -> PullRequestText:
        if request.title and request.description:
            return PullRequestText(request.title, request.description)
        self.checkout.fetch(self.remote, target)
        work_item = work_items.get_workitem(work_item_ids[0]) if work_item_ids else None
        fallback = PullRequestText.fallback(
            self.branch,
            work_item,
            self.checkout.commit_subjects(self.remote, target, self.branch),
        )
        return PullRequestText(
            request.title or fallback.title,
            request.description or fallback.description,
        )
