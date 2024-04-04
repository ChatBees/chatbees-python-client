from typing import List

from chatbees.client_models.collection import (
    Collection,
    describe_response_to_collection,
)
from chatbees.utils.config import Config

from chatbees.server_models.collection_api import (
    CreateCollectionRequest,
    ConfigureCollectionRequest,
    ListCollectionsRequest,
    ListCollectionsResponse,
    DeleteCollectionRequest,
    DescribeCollectionRequest,
    DescribeCollectionResponse,
)

__all__ = [
    "create_collection",
    "collection",
    "configure_collection",
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
        public_read=col.public_read)
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


def configure_collection(
    collection_name: str, public_read: bool = None, description: str = None):
    """
    Configure a collection.

    Args:
        collection_name (str): The name of the collection.
        public_read (bool): Enable/disable public_read for the collection.
        description (str): Update the description for the collection.
    """
    req = ConfigureCollectionRequest(
        namespace_name=Config.namespace,
        collection_name=collection_name)
    if public_read is not None:
        req.public_read = public_read
    if description is not None:
        req.description = description
    url = f'{Config.get_base_url()}/collections/configure'
    Config.post(url=url, data=req.model_dump_json())


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
