from typing import List
from chatbees.server_models.admin_api import CreateApiKeyRequest, CreateApiKeyResponse
from chatbees.server_models.ingestion_api import (
    ConnectorReference,
    ListConnectorsRequest,
    ListConnectorsResponse,
)
from chatbees.utils.config import Config

__all__ = ["init", "list_connectors"]


def init(
    api_key: str,
    account_id: str,
    namespace: str = Config.PUBLIC_NAMESPACE
):
    """
    Initialize the ChatBees client.

    Args:
        api_key (str): The API key to authenticate requests.
        account_id (str): The account ID.
        namespace (str, optional): The namespace to use.
    Raises:
        ValueError: If the provided config is invalid
    """
    Config.api_key = api_key
    Config.account_id = account_id
    Config.namespace = namespace
    Config.validate_setup()


def list_connectors() -> List[ConnectorReference]:
    url = f'{Config.get_base_url()}/connectors/list'
    req = ListConnectorsRequest()
    resp = Config.post(
        url=url,
        data=req.model_dump_json(),
    )
    return ListConnectorsResponse.model_validate(resp.json()).connectors
