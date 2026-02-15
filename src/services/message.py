import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, Optional
from uuid import uuid4


@dataclass
class MessageDTO:
    id: str
    role: Literal["assistant", "human"]
    text: str
    chat_id: str
    created_at: datetime.datetime


class MessageRepository(ABC):

    @abstractmethod
    async def get_all(self, **filters) -> list[MessageDTO]:
        raise NotImplementedError

    @abstractmethod
    async def add_one(self, data: MessageDTO) -> MessageDTO:
        raise NotImplementedError


class InMemoryMessageRepository(MessageRepository):
    _instance: Optional["MessageRepository"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._messages: list[MessageDTO] = []
            self._initialized = True

    async def get_all(self, **filters) -> list[MessageDTO]:
        users = []
        for user in self._messages:
            is_passed = True
            for filter_key, filter_value in filters.items():
                if getattr(user, filter_key) != filter_value:
                    is_passed = False
            if is_passed:
                users.append(user)
        return users

    async def add_one(self, data: MessageDTO) -> MessageDTO:
        self._messages.append(data)
        return data


class BaseMessageService(ABC):

    @abstractmethod
    async def get_history(self, chat_id: str, size: int = 20) -> list[MessageDTO]:
        raise NotImplementedError

    @abstractmethod
    async def create_message(self, role: Literal["assistant", "human"], text: str, chat_id: str) -> MessageDTO:
        raise NotImplementedError


class MessageService(BaseMessageService):

    def __init__(self, message_repo: MessageRepository):
        self._message_repo = message_repo

    async def get_history(self, chat_id: str, size: int = 20) -> list[MessageDTO]:
        messages = await self._message_repo.get_all(chat_id=chat_id)
        sorted_messages = sorted(messages, key=lambda m: m.created_at)
        return sorted_messages[-size:]

    async def create_message(self, role: Literal["assistant", "human"], text: str, chat_id: str) -> MessageDTO:
        message_id = str(uuid4())
        created_at = datetime.datetime.now()
        message = MessageDTO(
            id=message_id,
            role=role,
            text=text,
            chat_id=chat_id,
            created_at=created_at
        )
        created_message = await self._message_repo.add_one(message)
        return created_message