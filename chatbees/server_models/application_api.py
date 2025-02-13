import enum
from typing import List, Set, Optional

from pydantic import BaseModel

from chatbees.server_models.application import Application


class CreateApplicationRequest(BaseModel):
    namespace_name: str
    application: Application

class ListApplicationsRequest(BaseModel):
    namespace_name: str

class ListApplicationsResponse(BaseModel):
    applications: List[Application]


class DeleteApplicationRequest(BaseModel):
    namespace_name: str
    application_name: str

class ShareApplicationRequest(BaseModel):
    namespace_name: str
    application_name: str

    # Roles to share, unshare and public setting
    roles_to_share: Set[str] = set()
    roles_to_unshare: Set[str] = set()
    public: Optional[bool] = None

