import enum
from typing import Optional, Set

from pydantic import BaseModel

from chatbees.server_models.collection_api import ChatAttributes


class ApplicationType(str, enum.Enum):
    COLLECTION = 'COLLECTION'
    GPT = 'GPT'


class CollectionTarget(BaseModel):
    collection_name: str


class GPTTarget(BaseModel):
    provider: str
    model: str

class Application(BaseModel):
    application_name: str

    application_type: ApplicationType

    # Application target could be one of the supported targets
    application_target: str

    application_desc: Optional[str] = None

    # Chat-related attributes
    chat_attrs: Optional[ChatAttributes] = None

    """
    System-assigned fields below
    """

    # User ID of owner
    owner: str = ''

    # Whether this application is enabled.
    # An application is automatically disabled if application_target becomes
    # invalid
    enabled: bool = True

    # Server-assigned ID for this application
    application_id: str = ''

    # Whether this application is public
    public: bool = False

    # Whether this application is a shared publication
    shared_roles: Set[str] = set()

    created_on_ms: int = 0

    # This is the last-access timestamp.
    # Different users will see different timestamps, based on their own access history
    last_accessed_ms: int = 0

