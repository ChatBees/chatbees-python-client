from pydantic import BaseModel


class CreateApiKeyRequest(BaseModel):
    pass


class CreateApiKeyResponse(BaseModel):
    api_key: str
