from fastapi.routing import APIRouter

from src.api.hello import router as hello_router
from src.core.settings import get_settings


settings = get_settings()
routers = APIRouter()

routers.include_router(hello_router, tags=["hello"])
