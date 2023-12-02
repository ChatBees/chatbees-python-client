from typing import List

from nautilusdb.server_models.app_api import AskRequest, AskResponse, AnswerReference
from nautilusdb.utils.config import Config


def ask(
    project_name: str,
    collection_name: str,
    question: str,
    doc_name=None,
    history_messages=None,
) -> (str, List[AnswerReference]):
    url = f'{Config.get_base_url()}/qadocs/ask'

    req = AskRequest(
        project_name=project_name,
        collection_name=collection_name,
        doc_name=doc_name,
        question=question,
        history_messages=history_messages,
    )
    enforce_api_key = True

    # Only allow openai-web collection to be accessed without API key to
    # simplify demo.
    if collection_name == 'openai-web':
        enforce_api_key = False

    resp = Config.post(
        url=url,
        data=req.model_dump_json(),
        enforce_api_key=enforce_api_key
    )
    resp = AskResponse.model_validate(resp.json())

    unique_doc_names = {ref.doc_name for ref in resp.refs}

    return (
        resp.answer,
        [AnswerReference(doc_name=name) for name in unique_doc_names]
    )
