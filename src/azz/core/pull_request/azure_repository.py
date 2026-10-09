import re
from dataclasses import dataclass
from typing import Final, Self
from urllib.parse import quote, unquote

type RemoteUrl = str

REMOTE_PATTERNS: Final = (
    re.compile(r"v3/(?P<organization>[^/]+)/(?P<project>[^/]+)/(?P<name>[^/]+?)/?$"),
    re.compile(
        r"dev\.azure\.com/(?P<organization>[^/]+)/(?P<project>[^/]+)"
        r"/_git/(?P<name>[^/?#]+)"
    ),
    re.compile(
        r"//(?:[^@/]+@)?(?P<organization>[^./@]+)\.visualstudio\.com/"
        r"(?:DefaultCollection/)?(?P<project>[^/]+)/_git/(?P<name>[^/?#]+)"
    ),
)


@dataclass(frozen=True, slots=True)
class AzureRepository:
    organization: str
    project: str
    name: str

    @classmethod
    def from_remote_url(cls, url: RemoteUrl) -> Self:
        """Read the repository a git remote points at, over SSH or HTTPS."""
        for pattern in REMOTE_PATTERNS:
            if match := pattern.search(url.strip()):
                return cls(*(unquote(part) for part in match.groups()))
        raise ValueError(f"Not an Azure DevOps remote: {url}")

    @property
    def organization_url(self) -> str:
        return f"https://dev.azure.com/{self.organization}"

    def pull_request_url(self, pull_request_id: int) -> str:
        return (
            f"{self.organization_url}/{quote(self.project)}/_git/{quote(self.name)}"
            f"/pullrequest/{pull_request_id}"
        )
