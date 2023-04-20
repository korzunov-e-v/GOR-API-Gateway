from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI

from src.api.hello.schemas import Service
from src.core import get_settings
from src.core.utils import create_router_from_service
from src.core.utils import get_service_endpoints
from src.core.utils import read_default_services
from src.core.utils import write_services_to_file

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    default_services = read_default_services()
    services: List[Service] = []

    for d_serv in default_services:
        service = get_service_endpoints(d_serv)
        if service:
            services.append(service)

    app.state.services = services
    write_services_to_file(services)

    for serv in services:
        nested_router = create_router_from_service(serv)
        app.include_router(nested_router, prefix=settings.api_prefix)
    yield
