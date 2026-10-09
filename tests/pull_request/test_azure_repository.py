import pytest

from azz.core.pull_request.azure_repository import AzureRepository

EXPECTED = AzureRepository("contoso", "Web App", "web-app")


@pytest.mark.parametrize(
    "url",
    [
        "git@ssh.dev.azure.com:v3/contoso/Web%20App/web-app",
        "contoso@vs-ssh.visualstudio.com:v3/contoso/Web%20App/web-app",
        "https://contoso@dev.azure.com/contoso/Web%20App/_git/web-app",
        "https://dev.azure.com/contoso/Web%20App/_git/web-app",
        "https://contoso.visualstudio.com/Web%20App/_git/web-app",
        "https://contoso.visualstudio.com/DefaultCollection/Web%20App/_git/web-app",
    ],
)
def test_every_remote_form_names_the_same_repository(url: str) -> None:
    assert AzureRepository.from_remote_url(url) == EXPECTED


def test_a_foreign_remote_is_refused() -> None:
    with pytest.raises(ValueError, match="Not an Azure DevOps remote"):
        AzureRepository.from_remote_url("git@github.com:contoso/web-app.git")


def test_the_pull_request_url_quotes_the_project() -> None:
    assert EXPECTED.pull_request_url(7) == (
        "https://dev.azure.com/contoso/Web%20App/_git/web-app/pullrequest/7"
    )
