import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, Optional
from uuid import uuid4


@dataclass
class TransactionDTO:
    id: str
    user_id: str
    transaction_type: Literal["chat", "top_up"]
    value: int
    created_at: datetime.datetime


class TransactionRepository(ABC):

    @abstractmethod
    async def get_all(self, **filters) -> list[TransactionDTO]:
        raise NotImplementedError

    @abstractmethod
    async def add_one(self, data: TransactionDTO) -> TransactionDTO:
        raise NotImplementedError


class InMemoryTransactionRepository(TransactionRepository):
    _instance: Optional["InMemoryTransactionRepository"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._transactions: list[TransactionDTO] = []
            self._initialized = True

    async def get_all(self, **filters) -> list[TransactionDTO]:
        users = []
        for user in self._transactions:
            is_passed = True
            for filter_key, filter_value in filters.items():
                if getattr(user, filter_key) != filter_value:
                    is_passed = False
            if is_passed:
                users.append(user)
        return users

    async def add_one(self, data: TransactionDTO) -> TransactionDTO:
        self._transactions.append(data)
        return data


class BaseBillingService(ABC):

    @abstractmethod
    async def get_current_balance(self, user_id: str) -> int:
        raise NotImplementedError

    @abstractmethod
    async def create_transaction(self, user_id: str, transaction_type: Literal["chat", "top_up"], value: str) -> None:
        raise NotImplementedError


class BillingService(BaseBillingService):

    def __init__(self, transaction_repo: TransactionRepository):
        self._transaction_repo = transaction_repo

    async def get_current_balance(self, user_id: str) -> int:
        transactions = await self._transaction_repo.get_all(user_id=user_id)
        current_balance = sum(t.value for t in transactions)
        return current_balance

    async def create_transaction(self, user_id: str, transaction_type: Literal["chat", "top_up"], value: int) -> None:
        transaction_id = str(uuid4())
        created_at = datetime.datetime.now()
        transaction = TransactionDTO(
            id=transaction_id,
            user_id=user_id,
            transaction_type=transaction_type,
            value=value,
            created_at=created_at
        )
        await self._transaction_repo.add_one(transaction)