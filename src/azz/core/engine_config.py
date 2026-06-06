import os
from typing import Self

from pydantic import BaseModel, field_validator

ProjectName = str


class EngineConfig(BaseModel):
    org_url: str
    default_project: ProjectName
    management_project: ProjectName
    default_repo: str
    editor: str = "nvim"
    prepend_project_name: bool = True

    @field_validator("org_url", "default_project", "management_project", "default_repo")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Environment variable cannot be empty")
        return v.strip()

    @classmethod
    def from_env(cls) -> Self:
        return cls(
            org_url=os.getenv("AZURE_DEVOPS_ORG", ""),
            default_project=os.getenv("AZURE_DEVOPS_PROJECT", ""),
            management_project=os.getenv("AZURE_DEVOPS_MANAGEMENT_PROJECT", ""),
            default_repo=os.getenv("AZURE_DEVOPS_REPO", ""),
            editor=os.getenv("EDITOR", "nvim"),
            prepend_project_name=os.getenv(
                "AZZ_PREPEND_PROJECT_NAME", "true"
            ).lower() == "true",
        )

    @property
    def projects(self) -> tuple[ProjectName, ...]:
        return (self.default_project, self.management_project)

    model_config = {"arbitrary_types_allowed": True}
