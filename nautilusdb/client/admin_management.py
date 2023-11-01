from nautilusdb.server_models.api import CreateApiKeyRequest, CreateApiKeyResponse
from nautilusdb.utils.config import Config

__all__ = ["init", "create_api_key"]


def init(
    api_key: str = None,
    account_name: str = Config.PUBLIC_ACCOUNT
):
    """
    Initialize the NautilusDB client.

    Args:
        api_key (str, optional): The API key to authenticate requests.
                                 Defaults to None. You can still access
                                 public collections without an API key.
        account_name (str, optional): The name of the account. Defaults to
                                      Config.DEMO_ACCOUNT
    Raises:
        ValueError: If the provided config is invalid
    """
    Config.api_key = api_key
    Config.account_name = account_name
    Config.validate_setup()


def create_api_key() -> str:
    """
    Create a new APIKey in the configured account.

    Returns:
        The created API key

    """
    url = f'{Config.get_base_url()}/apikey/create'
    req = CreateApiKeyRequest()
    resp = Config.post(url=url, data=req.model_dump_json())
    return CreateApiKeyResponse.model_validate(resp.json()).api_key
