__all__ = ["create_gpt_application", "create_collection_application", "delete_application", "list_applications"]

from typing import Optional, List

from chatbees.server_models.application import (
    Application,
    ApplicationType,
    CollectionTarget,
    GPTTarget,
)
from chatbees.server_models.application_api import (
    CreateApplicationRequest,
    DeleteApplicationRequest, ListApplicationsResponse,
)
from chatbees.server_models.collection_api import ChatAttributes
from chatbees.utils.config import Config

def create_gpt_application(
    application_name: str,
    provider: str,
    model: str,
    description: Optional[str] = None,
    chat_attrs: Optional[ChatAttributes] = None
) -> Application:
    """
    Create a new collection application in ChatBees.

    """
    url = f'{Config.get_base_url()}/applications/create'
    application = Application(
        application_name=application_name,
        application_desc=description,
        application_type=ApplicationType.GPT,
        chat_attrs=chat_attrs,
        application_target=GPTTarget(
            provider=provider, model=model).model_dump_json())
    req = CreateApplicationRequest(application=application)
    Config.post(url=url, data=req.model_dump_json())
    return application

def create_collection_application(
    application_name: str,
    collection_name: str,
    description: Optional[str] = None,
    chat_attrs: Optional[ChatAttributes] = None
) -> Application:
    """
    Create a new collection application in ChatBees.

    """
    url = f'{Config.get_base_url()}/applications/create'
    application = Application(
        application_name=application_name,
        application_desc=description,
        application_type=ApplicationType.COLLECTION,
        chat_attrs=chat_attrs,
        application_target=CollectionTarget(
            namespace_name=Config.namespace, collection_name=collection_name).model_dump_json())
    req = CreateApplicationRequest(application=application)
    Config.post(url=url, data=req.model_dump_json())
    return application


def delete_application(application_name: str):
    """
    Deletes an application

    Args:
        application_name (str): The name of the application.
    """
    url = f'{Config.get_base_url()}/applications/delete'
    req = DeleteApplicationRequest(application_name=application_name)
    Config.post(url=url, data=req.model_dump_json())


def list_applications() -> List[Application]:
    """
    List all applications in account.

    Returns:
        List[Application]: A list of application objects.
    """
    url = f'{Config.get_base_url()}/applications/list'
    resp = Config.post(url=url)
    return ListApplicationsResponse.model_validate(resp.json()).applications
