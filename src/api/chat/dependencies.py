from typing import Annotated

from fastapi import Depends

from src.services.billing import TransactionRepository, InMemoryTransactionRepository, BaseBillingService, BillingService
from src.services.message import MessageRepository, InMemoryMessageRepository, MessageService, BaseMessageService
from src.services.llm import LLMService, OllamaLLMService

def get_message_repo() -> MessageRepository:
    return InMemoryMessageRepository()


def get_message_service(
    message_repo: MessageRepository = Depends(get_message_repo)
) -> BaseMessageService:
    return MessageService(message_repo)


def get_llm_service() -> LLMService:
    model_name = "llama3.2:3b"
    ollama_base_url = "http://localhost:11434"
    return OllamaLLMService(model_name, ollama_base_url)


def get_transaction_repo() -> TransactionRepository:
    return InMemoryTransactionRepository()


def get_billing_service(
    transaction_repo: TransactionRepository = Depends(get_transaction_repo)
) -> BaseBillingService:
    return BillingService(transaction_repo)


MessageServiceDependency = Annotated[BaseMessageService, Depends(get_message_service)]
LLMServiceDependency = Annotated[LLMService, Depends(get_llm_service)]
BillingServiceDependency = Annotated[BaseBillingService, Depends(get_billing_service)]