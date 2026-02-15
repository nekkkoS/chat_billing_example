from fastapi import FastAPI
from src.api.auth.endpoints import router as auth_router
from src.api.chat.endpoints import router as chat_router


app = FastAPI()
app.include_router(router=auth_router, prefix="/api/v1")
app.include_router(router=chat_router, prefix="/api/v1")