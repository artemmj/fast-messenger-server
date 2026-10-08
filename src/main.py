from fastapi import FastAPI, APIRouter

from routers.user import router as users_router


app = FastAPI(
    # title="CRM Service",
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
app.include_router(users_router)
