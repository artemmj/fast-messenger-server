from fastapi import FastAPI, APIRouter

from routers.user import router as users_router
from routers.auth import router as auth_router
from routers.chat import router as chat_router
from routers.chat_message import router as message_router


app = FastAPI(
    title="FastMessenger API",
    # root_path="/api/v1/crm",
    # docs_url="/docs",
    # redoc_url="/redoc",
    # openapi_url="/openapi.json",
)

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(chat_router)
app.include_router(message_router)
