from typing import List

from utils.config import Config
from utils.exceptions import Unimplemented
from client_models.vector import Vector
from server_models.api import UpsertRequest, UpsertResponse


class Collection:
    """
    Client-side Collection to decouple from API Collection
    """
    name: str

    def __init__(self, name):
        self.name = name

    def upsert_vector(self, vectors: List[Vector]) -> int:
        url = Config.get_base_url() + '/vectors/upsert'
        req = UpsertRequest(collection_name=self.name,
                            vectors=[v.to_api_vector() for v in vectors])
        resp = Config.post(url=url, data=req.model_dump_json())
        resp = UpsertResponse.model_validate_json(resp.json())
        return resp.upsert_count

    def delete_vector(self, vector_ids=List[str]):
        raise Unimplemented("delete_vector is not yet implemented")
