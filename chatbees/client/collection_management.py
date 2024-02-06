from typing import List

from chatbees.client_models.collection import (
    Collection,
    describe_response_to_collection,
)
from chatbees.utils.config import Config

from chatbees.server_models.collection_api import (
    CreateCollectionRequest,
    ListCollectionsRequest,
    ListCollectionsResponse,
    DeleteCollectionRequest,
    DescribeCollectionRequest,
    DescribeCollectionResponse,
)

__all__ = [
    "create_collection",
    "collection",
    "list_collections",
    "delete_collection",
    "describe_collection",
]


def create_collection(col: Collection) -> Collection:
    """
    Create a new collection in ChatBees.

    Args:
        col (Collection): The collection to create.
    Returns:
        The created collection

    """
    url = f'{Config.get_base_url()}/collections/create'
    req = CreateCollectionRequest(
        namespace_name=Config.namespace,
        collection_name=col.name,
        description=col.description,
        public_read=col.public_readable)
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


def list_collections() -> List[str]:
    """
    List all collections in ChatBees.

    Returns:
        List[Collection]: A list of collection objects.
    """
    url = f'{Config.get_base_url()}/collections/list'
    req = ListCollectionsRequest(namespace_name=Config.namespace)
    resp = Config.post(url=url, data=req.model_dump_json())
    return ListCollectionsResponse.model_validate(resp.json()).names


def delete_collection(collection_name: str):
    """
    Delete a collection from ChatBees.

    Args:
        collection_name (str): The name of the collection.
    """
    req = DeleteCollectionRequest(
        namespace_name=Config.namespace,
        collection_name=collection_name)
    url = f'{Config.get_base_url()}/collections/delete'
    Config.post(url=url, data=req.model_dump_json())


def describe_collection(collection_name: str) -> Collection:
    """
    Describe a collection.

    Args:
        collection_name (str): The name of the collection.
    Returns:
        Collection: A collection
    """

    req = DescribeCollectionRequest(
        namespace_name=Config.namespace,
        collection_name=collection_name)
    url = f'{Config.get_base_url()}/collections/describe'
    resp = DescribeCollectionResponse.model_validate(
        Config.post(url=url, data=req.model_dump_json()).json())
    return describe_response_to_collection(collection_name, resp)
