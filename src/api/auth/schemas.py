from uuid import uuid4
from pydantic import BaseModel, Field

from src.services.auth import UserDTO


class LoginRequest(BaseModel):
    username: str = Field(examples=["admin"])
    password: str = Field(examples=["admin"])


class UserMetadataSchema(BaseModel):
    ...

class LoginResponse(BaseModel):
    id: str = Field(examples=[str(uuid4())])
    display_name: str = Field(examples=["Admin"])
    metadata: UserMetadataSchema

    @classmethod
    def from_dto(cls, user: UserDTO) -> "LoginResponse":
        return cls(
            id=user.id,
            display_name=user.name,
            metadata=UserMetadataSchema()
        )


class RegisterRequest(BaseModel):
    name: str = Field(examples=["Admin"])
    username: str = Field(examples=["admin"])
    password: str = Field(examples=["admin"])


class UserResponseSchema(BaseModel):
    id: str = Field(examples=[str(uuid4())])
    display_name: str = Field(examples=["Admin"])
    metadata: UserMetadataSchema

    @classmethod
    def from_dto(cls, user: UserDTO) -> "UserResponseSchema":
        return cls(
            id=user.id,
            display_name=user.name,
            metadata=UserMetadataSchema()
        )