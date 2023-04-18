import requests
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from pydantic import ValidationError

from src.api.hello.schemas import HelloSchema
from src.api.hello.schemas import Service
from src.core.settings import get_settings
from src.core.utils import clear_app_routes
from src.core.utils import create_router_from_service
from src.core.utils import get_logger
from src.core.utils import write_services_to_file

router = APIRouter()
settings = get_settings()


@router.get("/hello/", name="hello:get_hello", response_model=HelloSchema)
async def get_hello(request: Request):
    """Hello healthcheck"""
    return {"message": "HELLO FROM API-Gateway Python, GET method"}


@router.post("/hello/", name="hello:post_hello", response_model=HelloSchema)
async def post_hello(service: Service, request: Request):
    """Get service info"""
    logger = get_logger(settings.logging_level)
    logger.info(f"post_hello: INFO: Connection request from {service.label}")
    url = (
        f"http://{service.label}:{service.port}"
        f"{settings.api_prefix}/endpoint-info/"
    )
    try:
        resp = requests.get(url=url, timeout=5)
        resp_service = Service(**resp.json())
    except requests.exceptions.ConnectionError:
        logger.warning(
            f"post_hello: ERROR: Connection failed with {service.label}"
        )
        raise HTTPException(400, "bad request, connection timeout")
    except ValidationError:
        logger.warning(
            f"post_hello: ERROR: Connection failed with {service.label}"
        )
        raise HTTPException(400, "bad request, validation error")

    services = request.app.state.services
    for i, serv in enumerate(services):
        if resp_service.name == serv.name:
            del services[i]
    services.append(resp_service)

    write_services_to_file(services)
    clear_app_routes(request.app)

    for serv in services:
        nested_router = create_router_from_service(serv)
        request.app.include_router(nested_router, prefix=settings.api_prefix)

    logger.info(f"post_hello: INFO: Success connection with {service.label}")
    request.app.state.services = services
    return {"message": "HELLO FROM API-Gateway Python, POST method"}
