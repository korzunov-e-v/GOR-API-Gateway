import datetime
import json
import logging
import socket
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import Message

from src.core.settings import get_settings
from src.core.utils import get_logger

settings = get_settings()


class RequestIDMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        headers = scope.get("headers")
        if headers:
            headers = dict(headers)
            headers[b"x-request-id"] = str(uuid.uuid4()).encode()
            scope["headers"] = [(k, v) for k, v in headers.items()]
        await self.app(scope, receive, send)


class RequestLogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def set_body(self, request: Request):
        receive_ = await request._receive()

        async def receive() -> Message:
            return receive_

        request._receive = receive

    async def dispatch(self, request: Request, call_next):
        log = get_logger(settings.logging_level)
        start_time = time.time()
        timestamp = datetime.datetime.now().isoformat(timespec="milliseconds")

        log_data = {
            "ts": timestamp,
            "level": logging.getLevelName(log.getEffectiveLevel()),
            "remote_address": request.client.host,
            "server_hostname": socket.gethostname(),
            "request_method": request.method,
            "url": request.url.path,
            "request_id": request.headers.get("X-Request-Id"),
        }

        await self.set_body(request)
        body = await request.body()

        if "/api/" in str(request.url.path):
            try:
                req_body = json.loads(body.decode("utf-8")) if body else {}
                log_data["request_body"] = req_body
            except json.JSONDecodeError:
                log.warning("RequestLogMiddleware: WARNING: cant decode body")
                log.warning(f"RequestLogMiddleware: WARNING: body: {body}")
                log_data["request_body"] = {body}

        response = await call_next(request)

        log_data["request_status"] = response.status_code
        log_data["took"] = time.time() - start_time
        log.info(msg=log_data)
        return response
