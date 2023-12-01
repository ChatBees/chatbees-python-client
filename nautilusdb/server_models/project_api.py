from typing import List

from pydantic import BaseModel


class CreateProjectRequest(BaseModel):
    project_name: str


class CreateProjectResponse(BaseModel):
    pass


class DeleteProjectRequest(BaseModel):
    project_name: str


class DeleteProjectResponse(BaseModel):
    pass


class ListProjectsRequest(BaseModel):
    pass


class ListProjectsResponse(BaseModel):
    names: List[str]
