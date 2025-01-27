import enum
from typing import List

from pydantic import BaseModel

from chatbees.server_models.application import Application


class CreateApplicationRequest(BaseModel):
    application: Application


class ListApplicationsResponse(BaseModel):
    applications: List[Application]


class DeleteApplicationRequest(BaseModel):
    application_name: str
