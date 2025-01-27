import enum
from typing import Optional

from pydantic import BaseModel

from chatbees.server_models.collection_api import ChatAttributes


class ApplicationType(str, enum.Enum):
    COLLECTION = 'COLLECTION'
    GPT = 'GPT'


class CollectionTarget(BaseModel):
    namespace_name: str
    collection_name: str


class GPTTarget(BaseModel):
    provider: str
    model: str

class Application(BaseModel):
    application_name: str

    application_desc: Optional[str] = ''

    application_type: ApplicationType

    enabled: bool = True

    application_target: str

    chat_attrs: Optional[ChatAttributes] = None


