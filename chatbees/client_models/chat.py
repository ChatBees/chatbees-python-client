from typing import Optional, List, Tuple

from pydantic import BaseModel

from chatbees.server_models.conversation import (
    ConversationMeta,
    ListConversationsRequest,
    ListConversationsResponse, GetConversationRequest, GetConversationResponse,
)
from chatbees.server_models.doc_api import AskResponse
from chatbees.utils.ask import ask, ask_application
from chatbees.utils.config import Config

__all__ = ["Chat"]


class Chat(BaseModel):
    """
    A new chatbot instance that supports conversational Q and A.
    """
    namespace_name: Optional[str] = None
    collection_name: Optional[str] = None
    application_name: Optional[str] = None
    doc_name: Optional[str] = None
    history_messages: Optional[List[Tuple[str, str]]] = None
    conversation_id: Optional[str] = None

    def _validate_names(self):
        if self.application_name is not None and self.namespace_name is None and self.collection_name is None:
            return
        if self.application_name is None and self.namespace_name is not None and self.collection_name is not None:
            return
        raise ValueError(f"Chat must specify either both namespace and collection, or application")

    @classmethod
    def list_conversations(cls, collection_name=None, application_name=None) -> List[ConversationMeta]:
        url = f'{Config.get_base_url()}/conversations/list'
        namespace = Config.namespace if collection_name is not None else None
        req = ListConversationsRequest(
            namespace_name=namespace,
            collection_name=collection_name,
            application_name=application_name
        )
        resp = Config.post(
            url=url,
            data=req.model_dump_json(),
        )
        return ListConversationsResponse.model_validate(resp.json()).conversations

    @classmethod
    def from_conversation(cls, conversation_id, collection_name=None, application_name=None) -> "Chat":
        url = f'{Config.get_base_url()}/conversations/get'
        req = GetConversationRequest(
            conversation_id=conversation_id,
        )
        resp = Config.post(
            url=url,
            data=req.model_dump_json(),
        )
        chat = Chat()
        convos = GetConversationResponse.model_validate(resp.json()).conversation
        chat.conversation_id = conversation_id
        chat.collection_name = collection_name
        chat.application_name = application_name

        # TODO: Fix this convoluted logic...openai accepts a plain array of
        #  {role, content}. Simply preserve this and pass it over to openai
        paired_content = [(convos.messages[i].content, convos.messages[i + 1].content) for i in
                          range(0, len(convos.messages) - 1, 2)]
        chat.history_messages = paired_content
        return chat


    def ask(self, question: str, top_k: int = 5) -> AskResponse:
        self._validate_names()

        if self.application_name is None:
            resp = ask(
                Config.namespace,
                self.collection_name,
                question,
                top_k,
                doc_name=self.doc_name,
                history_messages=self.history_messages,
                conversation_id=self.conversation_id,
            )
        else:
            resp = ask_application(
                self.application_name,
                question,
                top_k,
                doc_name=self.doc_name,
                history_messages=self.history_messages,
                conversation_id=self.conversation_id,
            )

        if self.history_messages is None:
            self.history_messages = []
        self.history_messages.append((question, resp.answer))
        if self.conversation_id is None:
            self.conversation_id = resp.conversation_id
        return resp
