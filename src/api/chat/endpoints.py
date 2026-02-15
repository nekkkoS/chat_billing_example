from fastapi import APIRouter, Body, status, Path
from fastapi.responses import JSONResponse

from src.api.auth.dependencies import CurrentUserDependency, AuthServiceDependency
from src.api.general_schemas import ErrorResponse, SuccessResponse
from src.api.chat.dependencies import MessageServiceDependency, LLMServiceDependency, BillingServiceDependency
from src.api.chat.schemas import NewMessageRequest, NewMessageResponse, TopUpRequest

router = APIRouter(prefix="", tags=["chat_billing"])


@router.post("/chat/{chat_id}/messages", response_model=NewMessageResponse)
async def handle_user_message(
    message_service: MessageServiceDependency,
    billing_service: BillingServiceDependency,
    llm_service: LLMServiceDependency,
    user: CurrentUserDependency,
    chat_id: str = Path(),
    data: NewMessageRequest = Body(),
) -> JSONResponse:
    if not user:
        return JSONResponse(
            content=ErrorResponse(message="Требуется войти в аккаунт").model_dump(),
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    balance = await billing_service.get_current_balance(user.id)
    if balance <= 0:
        return JSONResponse(
            content=ErrorResponse(message=f"Требуется пополнить баланс, ваш текущий баланс: {balance}").model_dump(),
            status_code=status.HTTP_409_CONFLICT
        )
    history = await message_service.get_history(chat_id, size=20)
    answer = await llm_service.execute(text=data.text, history=[(m.role, m.text) for m in history])
    await message_service.create_message("human", data.text, chat_id)
    await message_service.create_message("assistant", answer.text, chat_id)
    await billing_service.create_transaction(user.id, "chat", -1 * answer.used_tokens)
    return JSONResponse(content=NewMessageResponse.from_dto(answer).model_dump(), status_code=status.HTTP_200_OK)


@router.post("/users/{user_id}/balance/top-up", response_model=SuccessResponse)
async def top_up_user_balance(
    billing_service: BillingServiceDependency,
    auth_service: AuthServiceDependency,
    user_id: str = Path(),
    data: TopUpRequest = Body(),
) -> JSONResponse:
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        return JSONResponse(
            content=ErrorResponse(message="Пользователь не существует").model_dump(),
            status_code=status.HTTP_404_NOT_FOUND
        )
    await billing_service.create_transaction(user.id, "top_up", data.value)
    return JSONResponse(content=SuccessResponse(message="Успешное пополнение").model_dump(), status_code=status.HTTP_201_CREATED)