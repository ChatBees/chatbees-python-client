from typing import List

from nautilusdb.server_models.doc_api import AskRequest, AskResponse, AnswerReference
from nautilusdb.utils.config import Config


def ask(
    project_name: str,
    collection_name: str,
    question: str,
    doc_name=None,
    history_messages=None,
) -> (str, List[AnswerReference]):
    url = f'{Config.get_base_url()}/docs/ask'

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

    return (
        resp.answer,
        [AnswerReference(doc_name=ref.doc_name,
                         page_num=ref.page_num,
                         sample_text=ref.sample_text) for ref in resp.refs]
    )
