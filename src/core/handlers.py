import httpx
from httpx import AsyncClient

from fastapi import Request
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

HTTP_SERVER = AsyncClient(base_url="http://localhost:8000/")


def dynamic_handler(host_port: str):
    async def _reverse_proxy(request: Request):
        url = httpx.URL(
            url=f'{host_port}',
            path=request.url.path,
            query=request.url.query.encode("utf-8")
        )
        rp_req = HTTP_SERVER.build_request(
            method=request.method,
            url=url,
            headers=request.headers,
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
