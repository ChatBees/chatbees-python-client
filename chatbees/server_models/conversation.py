from typing import List

from pydantic import BaseModel

from chatbees.server_models.collection_api import CollectionBaseRequest


# OpenAI: https://cdn.openai.com/spec/model-spec-2024-05-08.html#follow-the-chain-of-command
# Llama3:https://www.llama.com/docs/model-cards-and-prompt-formats/llama3_1/#prompt-template
class Message(BaseModel):
    timestamp: int
    request_id: str

    # Openai: user, assistant, tool etc
    # Llama: system, user, assistant, ipython, etc
    role: str
    content: str


class ConversationMeta(BaseModel):
    conversation_id: str
    title: str
    start_ts: int

    # Source of the conversation.
    # e.g. clid, app_id, clid/doc_id
    source_id: str

class Conversation(BaseModel):
    meta: ConversationMeta
    messages: List[Message]

    def append(self, messages: List[Message]):
        # In most cases, we'll be inserting 2 messages at the end, so
        # efficiency does not matter
        for msg in messages:
            insert_index = len(self.messages)

            # Ensure messages are in chronological order
            while insert_index > 0 and msg.timestamp < self.messages[insert_index - 1].timestamp:
                insert_index -= 1

            self.messages.insert(insert_index, msg)

class ListConversationsRequest(CollectionBaseRequest):
    pass


class ListConversationsResponse(BaseModel):
    conversations: List[ConversationMeta]


class GetConversationRequest(BaseModel):
    conversation_id: str


class GetConversationResponse(BaseModel):
    conversation: Conversation
