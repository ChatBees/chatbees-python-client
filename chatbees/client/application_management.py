__all__ = ["create_application", "delete_application", "list_applications"]

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
from chatbees.utils.config import Config

def create_application(
    application_name: str,
    application_type: ApplicationType,
    **kwargs
) -> Application:
    """
    Create a new application in ChatBees.

    Args:
        application_name: The name of the application
        application_type: Application type

    KwArgs:
        collection_name: Collection to target (CollectionTarget only)
        provider: Provider of GPT application (GPT application only)
        model: Model of GPT application (GPT application only)
    Returns:
        The created application

    """
    url = f'{Config.get_base_url()}/applications/create'
    application: Optional[Application] = None
    req: Optional[CreateApplicationRequest] = None

    match application_type:
        case ApplicationType.COLLECTION:
            assert set(kwargs.keys()) == {'collection_name'}, f"Invalid keyword args"
            params = {**kwargs, "namespace_name": Config.namespace}
            application = Application(
                application_name=application_name,
                application_type=application_type,
                application_target=CollectionTarget(**params).model_dump_json())
            req = CreateApplicationRequest(application=application)
        case ApplicationType.GPT:
            assert set(kwargs.keys()) == {'provider', 'model'}, f"Invalid keyword args"
            application = Application(
                application_name=application_name,
                application_type=application_type,
                application_target=GPTTarget(**kwargs).model_dump_json())
            req = CreateApplicationRequest(application=application)
        case _:
            raise ValueError(f"Invalid application type {application_type}")
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
