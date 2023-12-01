from typing import List

from nautilusdb.server_models.project_api import (
    CreateProjectRequest,
    DeleteProjectRequest,
    ListProjectsRequest, ListProjectsResponse,
)
from nautilusdb.utils.config import Config

__all__ = ["create_project", "list_projects", "delete_project"]

def create_project(project_name: str):
    """
    Create a new project in the configured account.
    """
    url = f'{Config.get_base_url()}/projects/create'
    req = CreateProjectRequest(project_name=project_name)
    Config.post(
        url=url,
        data=req.model_dump_json(),
    )


def list_projects() -> List[str]:
    """
    Lists projects in the configured account.
    """
    url = f'{Config.get_base_url()}/projects/list'
    req = ListProjectsRequest()
    resp = Config.post(url=url, data=req.model_dump_json())
    return ListProjectsResponse.model_validate(resp.json()).names


def delete_project(project_name: str):
    """
    Deletes a project in the configured account.
    """
    url = f'{Config.get_base_url()}/projects/delete'
    req = DeleteProjectRequest(project_name=project_name)
    Config.post(
        url=url,
        data=req.model_dump_json(),
    )
