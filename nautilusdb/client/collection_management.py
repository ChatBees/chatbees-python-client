from typing import List

from nautilusdb.client_models.collection import Collection
from nautilusdb.utils.config import Config

from nautilusdb.server_models.api import (
    CreateCollectionRequest,
    ListCollectionsResponse,
    DeleteCollectionRequest,
)

__all__ = [
    "create_collection",
    "collection",
    "list_collections",
    "delete_collection",
]


def create_collection(col: Collection) -> Collection:
    """
    Create a new collection in NautilusDB.

    Args:
        col (Collection): The collection to create.
    Returns:
        The created collection

    """
    url = f'{Config.get_base_url()}/collections/create'
    req = CreateCollectionRequest(
        name=col.name,
        dimension=col.dimension,
        description=col.description,
        metas=col.metadata_columns)
    Config.post(url=url, data=req.model_dump_json())
    return col


def collection(collection_name: str) -> Collection:
    """
    Initializes a collection by name.

    Args:
        collection_name (str): The name of the collection.

    Returns:
        Collection: The collection object.
    """
    return Collection(name=collection_name)


def list_collections() -> List[Collection]:
    """
    List all collections in NautilusDB.

    Returns:
        List[Collection]: A list of collection objects.
    """
    url = f'{Config.get_base_url()}/collections/list'
    resp = Config.get(url=url)
    return [Collection(name=name) for name in
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
