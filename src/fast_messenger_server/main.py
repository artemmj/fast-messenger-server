from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from routers.user import router as users_router
from routers.auth import router as auth_router
from routers.chat import router as chat_router
from routers.chat_message import router as message_router


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # "https://your-production-app.com"
]

app = FastAPI(
    title="FastMessenger API",
    # root_path="/api/v1/crm",
    # docs_url="/docs",
    # redoc_url="/redoc",
    # openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Или ["*"] для открытия доступа вообще всем (не рекомендуется для продакшена)
    allow_credentials=True,  # Разрешить передачу cookies / auth-заголовков
    allow_methods=[
        "*"
    ],  # Разрешить ВСЕ методы, включая POST, GET, и критически важный OPTIONS
    allow_headers=["*"],  # Разрешить любые HTTP-заголовки
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
