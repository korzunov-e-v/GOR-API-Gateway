import json
import logging
from typing import List
from typing import Union

import logging_json
import requests
from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI

from src.api.hello.schemas import Service
from src.core import get_settings
from src.core.dependencies import jwt_validator
from src.core.handlers import dynamic_handler

settings = get_settings()


def protected_http_method(func):
    """Decorate your controller function with
    this decorator if requested user must
    be authorized.

    """
    func.__setattr__("protected", True)

    def inner(*args, **kwargs):
        return func(args, kwargs)

    return inner


def get_logger(level: Union[str, int]) -> logging.Logger:
    """
    Creates a JSON format Logger according to the Settings
    """
    middleware_logger = logging.getLogger(__name__)
    middleware_logger.setLevel(level)
    if not middleware_logger.handlers:
        st_formatter = logging_json.JSONFormatter()
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(st_formatter)
        middleware_logger.addHandler(stream_handler)
    return middleware_logger


def read_default_services() -> List[Service]:
    """
    Reads services from services_default.json
    """
    default_services: List[Service] = []
    with open("services_default.json", "r", encoding="utf-8") as file:
        data_dict = json.load(file)
        for serv_dict in data_dict:
            service = Service(**serv_dict)
            default_services.append(service)
    return default_services


def get_service_endpoints(service: Service) -> Union[Service, None]:
    """
    Get service with endpoints from service without endpoints
    """
    logger = get_logger(settings.logging_level)
    url = (
        f"http://{service.label}:{service.port}"
        f"{settings.api_prefix}/endpoint-info/"
    )
    try:
        resp = requests.get(url=url)
    except requests.exceptions.ConnectionError:
        logger.warning(
            f"lifespan: WARNING: Connection failed with {service.label}"
        )
        return None
    logger.info(f"lifespan: OK: Response from {service.label}")
    try:
        resp_json = resp.json()
    except requests.exceptions.JSONDecodeError:
        logger.warning(
            f"lifespan: WARNING: Service {service.label} returned bad response"
        )
        return None
    return Service(**resp_json)


def create_router_from_service(service: Service) -> APIRouter:
    """
    Creates and return router from endpoints of service
    """
    nested_router = APIRouter()
    host_port = f"http://{service.label}:{service.port}"
    for i, endp in enumerate(service.endpoints):  # type: ignore
        dependencies = []
        if endp.protected:
            dependencies = [Depends(jwt_validator)]
        nested_router.add_api_route(
            path=f"/{endp.url}",
            endpoint=dynamic_handler(host_port=host_port),
            methods=endp.methods,
            name=f"service_{service.label}_{i}",
            dependencies=dependencies,
        )
    return nested_router


def write_services_to_file(services: List[Service]):
    """
    Write all services to a file services.json (for debug)
    """
    services_json = []
    for serv in services:
        serv_json = json.dumps(serv.__dict__, default=lambda o: o.__dict__)
        services_json.append(json.loads(serv_json))

    with open("services.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(services_json, indent=4))


def clear_app_routes(app: FastAPI):
    """
    Clear all app routes except built-in
    """
    for i, route in reversed(list(enumerate(app.routes))):
        if "service" in route.name:
            del app.routes[i]
