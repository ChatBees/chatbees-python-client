from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


class CreateApiKeyRequest(BaseModel):
    pass


class CreateApiKeyResponse(BaseModel):
    api_key: str

class RoleType(str, Enum):
    # Built-in roles with fixed permissions
    AccountAdmin = "AccountAdmin"
    AccountUser = "AccountUser"

class Names(BaseModel):
    name: str
    given_name: Optional[str] = None
    middle_name: Optional[str] = None
    family_name: Optional[str] = None

class UserMetadata(BaseModel):
    # User creation time in nanoseconds since epoch
    ctime: int
    email: str
    names: Optional[Names] = None

class ClientUser(BaseModel):
    """
    Client-facing user model

    ID corresponds to "email" filed in the internal user model
    """
    id: str

    # System role
    role: RoleType

    # Custom roles
    custom_roles: List[str] = []
    metadata: UserMetadata

class AccountLoginResponse(BaseModel):
    # the unique account id. The rest requests for the account will be like
    # account_id.us-west-2.aws.chatbees.ai
    account_id: str
    # a short-live api key that UI can use to send the rest requests.
    shortlive_api_key: str
    # Stripe customer ID
    stripe_customer_id: str
    # user info
    user: Optional[ClientUser] = None
    # Default namespace
    default_namespace: str

class EmailAccountRequest(BaseModel):
    email: str
    password: str

