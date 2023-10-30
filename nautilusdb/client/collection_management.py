import os
import sys
from typing import List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from client_models.collection import Collection
from utils.config import Config

from server_models.api import (
    CreateCollectionRequest,
    ListCollectionsResponse,
    DeleteCollectionRequest,
)


def create_collection(col: Collection):
    """
    Create a new collection in NautilusDB.

    Args:
        col (Collection): The collection to create.

    """
    url = f'{Config.get_base_url()}/collections/create'
    req = CreateCollectionRequest(
        name=col.name,
        dimension=col.dimension,
        description=col.description,
        metas=col.metadata_columns)
    Config.post(url=url, data=req.model_dump_json())


def collection(collection_name: str) -> Collection:
    """
    Get a collection by name.

    Args:
        collection_name (str): The name of the collection.

    Returns:
        Collection: The collection object.
    """
    return Collection(collection_name)


def list_collections() -> List[Collection]:
    """
    List all collections in NautilusDB.

    Returns:
        List[Collection]: A list of collection objects.
    """
    url = f'{Config.get_base_url()}/collections/list'
    resp = Config.get(url=url)
    return [Collection(name) for name in
            ListCollectionsResponse.model_validate(resp.json()).names]


def delete_collection(collection_name: str):
    """
    Delete a collection from NautilusDB.

    Args:
        collection_name (str): The name of the collection.
    """
    req = DeleteCollectionRequest(name=collection_name)
    url = f'{Config.get_base_url()}/collections/delete'
    Config.post(url=url, data=req.model_dump_json())
