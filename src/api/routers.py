from fastapi.routing import APIRouter
from src.core.settings import get_settings

# from src.api.depositproducts import router as routers_depositproducts


settings = get_settings()
routers = APIRouter()

# routers.include_router(routers_depositproducts, tags=["deposit_products"])
