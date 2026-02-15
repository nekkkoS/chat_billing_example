from pydantic import BaseModel, Field

from src.services.llm import AnswerDTO


class NewMessageRequest(BaseModel):
    text: str = Field(examples=["HI, how are you?"])


class NewMessageResponse(BaseModel):
    text: str = Field(examples=["HI, how are you?"])
    used_tokens: int = Field(examples=[430])

    @classmethod
    def from_dto(cls, answer: AnswerDTO) -> "NewMessageResponse":
        return cls(
            text=answer.text,
            used_tokens=answer.used_tokens,
        )


class TopUpRequest(BaseModel):
    value: int = Field(examples=[100])