import enum

from pydantic import BaseModel


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

    application_type: ApplicationType

    # Application target could be one of the supported targets
    application_target: str
