from chatbees.server_models.admin_api import CreateApiKeyRequest, CreateApiKeyResponse
from chatbees.utils.config import Config

__all__ = ["init", "create_api_key"]


def init(
    api_key: str = None,
    account_id: str = Config.PUBLIC_ACCOUNT_ID,
    namespace: str = Config.PUBLIC_NAMESPACE
):
    """
    Initialize the ChatBees client.

    Args:
        api_key (str, optional): The API key to authenticate requests.
                                 Defaults to None. You can still access
                                 public collections without an API key.
        account_id (str, optional): The account ID. Defaults to "public".
        namespace (str, optional): The namespace to use.
    Raises:
        ValueError: If the provided config is invalid
    """
    Config.api_key = api_key
    Config.account_id = account_id
    Config.namespace = namespace
    Config.validate_setup()


def create_api_key() -> str:
    """
    Create a new APIKey in the public account.

    Returns:
        The created API key

    """
    if Config.account_id != Config.PUBLIC_ACCOUNT_ID:
        raise ValueError(
            "Please log in and create API key on UI for the private account")

    url = f'{Config.get_base_url()}/apikey/create'
    req = CreateApiKeyRequest()
    resp = Config.post(
        url=url,
        data=req.model_dump_json(),
        enforce_api_key=False,
    )
    return CreateApiKeyResponse.model_validate(resp.json()).api_key
