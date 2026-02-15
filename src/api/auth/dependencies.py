from typing import Optional, Annotated

from fastapi import Header, Depends

from src.services.auth import UserRepository, InMemoryUserRepository, BaseAuthService, AuthService, UserDTO


def get_user_repo() -> UserRepository:
    return InMemoryUserRepository()


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo)
) -> BaseAuthService:
    return AuthService(user_repo)


async def get_current_user(
    user_id: Optional[str] = Header(alias="X-User-Id", default=None),
    auth_service: BaseAuthService = Depends(get_auth_service),
) -> Optional[UserDTO]:
    if not user_id:
        return None
    user = await auth_service.get_user_by_id(user_id)
    return user


CurrentUserDependency = Annotated[UserDTO, Depends(get_current_user)]
AuthServiceDependency = Annotated[BaseAuthService, Depends(get_auth_service)]