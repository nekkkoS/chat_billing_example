from typing import Literal, cast
from abc import ABC, abstractmethod
from dataclasses import dataclass

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


HistoryType = list[tuple[Literal["assistant", "human"], str]]


@dataclass
class AnswerDTO:
    text: str
    used_tokens: int


class LLMService(ABC):

    @abstractmethod
    async def execute(self, text: str, history: HistoryType) -> AnswerDTO:
        raise NotImplementedError


class OllamaLLMService(LLMService):
    _MESSAGES = [
        ("system", "You are friendly assistant"),
        MessagesPlaceholder("history"),
        ("human", "{question}"),
    ]

    def __init__(self, model_name: str, ollama_base_url: str):
        llm = ChatOpenAI(
            model=model_name,
            base_url=f"{ollama_base_url}/v1",
            api_key="ollama",
        )
        prompt = ChatPromptTemplate(self._MESSAGES)
        self._chain = prompt | llm

    async def execute(self, text: str, history: HistoryType) -> AnswerDTO:
        response = await self._chain.ainvoke({
            "question": text,
            "history": history
        })
        response = cast(AIMessage, response)
        return AnswerDTO(
            text=response.content,
            used_tokens=response.usage_metadata.get("output_tokens", 0)
        )