import uuid


class RequestIDMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        headers = dict(scope["headers"])
        headers[b"x-request-id"] = str(uuid.uuid4()).encode()
        scope["headers"] = [(k, v) for k, v in headers.items()]
        await self.app(scope, receive, send)
