from typing import List, Tuple

from chatbees.server_models.doc_api import AskRequest, AskResponse, AnswerReference
from chatbees.utils.config import Config


def ask(
    namespace_name: str,
    collection_name: str,
    question: str,
    top_k: int = 5,
    doc_name: str = None,
    history_messages: List[Tuple[str, str]] = None,
    conversation_id: str = None,
) -> AskResponse:
    url = f'{Config.get_base_url()}/docs/ask'

    req = AskRequest(
        namespace_name=namespace_name,
        collection_name=collection_name,
        question=question,
        top_k=top_k,
        doc_name=doc_name,
        history_messages=history_messages,
        conversation_id=conversation_id,
    )

    resp = Config.post(
        url=url,
        data=req.model_dump_json(),
        enforce_api_key=False
    )
    return AskResponse.model_validate(resp.json())
