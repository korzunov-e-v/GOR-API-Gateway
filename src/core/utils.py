import json
import logging
from contextlib import asynccontextmanager
from typing import List

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


def get_logger(level: str | int) -> logging.Logger:
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = get_logger(settings.logging_level)

    app.state.services = []
    saved_services = []
    services: List[Service] = []
    with open("services.json", "w") as file:
        data = file.read()
        if data:
            data_dict = json.loads(data)
            for serv_dict in data_dict:
                service = Service(**serv_dict)
                saved_services.append(service)

    nested_router = APIRouter()
    for serv in saved_services:
        url = (
            f"http://{serv.ip}:{serv.port}"
            f"{settings.api_prefix}/endpoint-info/"
        )
        try:
            resp = requests.get(url=url)
        except requests.exceptions.ConnectionError:
            logger.info(f"lifespan: Connection failed with {serv.label}")
            continue
        resp_service = Service(**resp.json())

        host_port = f"http://{resp_service.ip}:{resp_service.port}"
        for i, endp in enumerate(serv.endpoints):  # type: ignore
            dependencies = []
            if endp.protected:
                dependencies = [Depends(jwt_validator)]
            nested_router.add_api_route(
                path=f"/{endp.url}",
                endpoint=dynamic_handler(host_port=host_port),
                methods=endp.methods,
                name=f"{serv.label}_{i}",
                dependencies=dependencies,
            )

    app.include_router(nested_router, prefix=settings.api_prefix)
    app.state.services = services
    yield
