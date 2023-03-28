import json
import httpx
from fastapi.routing import APIRoute
from httpx import AsyncClient
import requests

from starlette.background import BackgroundTask
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from src.api.hello.schemas import HelloSchema, Service
from src.core.settings import get_settings


router = APIRouter()
settings = get_settings()

HTTP_SERVER = AsyncClient(base_url="http://localhost:8000/")


def dynamic_handler(host_port: str):
    async def _reverse_proxy(request: Request):
        url = httpx.URL(
            url=f'{host_port}',
            path=request.url.path,
            query=request.url.query.encode("utf-8")
        )
        rp_req = HTTP_SERVER.build_request(
            request.method, url, headers=request.headers.raw,
            content=await request.body()
        )
        rp_resp = await HTTP_SERVER.send(rp_req, stream=True)
        return StreamingResponse(
            rp_resp.aiter_raw(),
            status_code=rp_resp.status_code,
            headers=rp_resp.headers,
            background=BackgroundTask(rp_resp.aclose),
        )

    return _reverse_proxy


@router.get(
    "/hello/",
    name="hello:get_hello",
    response_model=HelloSchema
)
async def get_hello(request: Request):
    """Hello healthcheck"""
    return {'message': 'HELLO FROM API-Gateway Python, GET method'}


@router.post(
    "/hello/",
    name="hello:post_hello",
    response_model=HelloSchema
)
async def post_hello(service: Service, request: Request):
    """Get service info"""
    url = f'http://{service.ip}:{service.port}' \
          f'{settings.api_prefix}/endpoint-info/'
    resp = requests.get(url=url)
    resp_service = Service(**resp.json())

    services = request.app.state.services
    nested_router = APIRouter()
    for i, serv in enumerate(services):
        if resp_service.name == serv.name:
            del services[i]
    services.append(resp_service)

    services_json = []
    for serv in services:
        serv_json = json.dumps(serv.__dict__, default=lambda o: o.__dict__)
        services_json.append(json.loads(serv_json))

    with open('services.json', 'w') as file:
        file.write(json.dumps(services_json, indent=4))

    for i, route in reversed(list(enumerate(request.app.routes))):
        if isinstance(route, APIRoute) and 'hello' not in route.name:
            del request.app.routes[i]

    for serv in services:
        host_port = f'http://{serv.ip}:{serv.port}'
        for i, endp in enumerate(serv.endpoints):
            nested_router.add_api_route(
                path=f'/{endp.url}',
                endpoint=dynamic_handler(host_port=host_port),
                methods=endp.methods,
                name=f'{serv.label}_{i}'
            )

    request.app.include_router(
        nested_router,
        prefix=settings.api_prefix
    )
    request.app.state.services = services
    return {'message': 'HELLO FROM API-Gateway Python, POST method'}
