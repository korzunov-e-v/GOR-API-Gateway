from datetime import datetime

import jwt
import pytz
from dateutil.parser import parse
from fastapi import HTTPException
from fastapi import Request
from starlette.datastructures import MutableHeaders

from src.core.settings import get_settings

settings = get_settings()


async def jwt_validator(request: Request):
    try:
        jwt_token = request.headers["Authorization"].split()[1]
    except KeyError:
        raise HTTPException(401, "unauthorized")
    try:
        jwt_parsed = jwt.decode(
            jwt_token, key=settings.secret_jwt, algorithms=["HS256"]
        )
    except jwt.InvalidTokenError:
        raise HTTPException(401, "invalid token")
    exp_at = parse(jwt_parsed["expiredAt"])
    if exp_at < datetime.now(tz=pytz.utc):
        raise HTTPException(401, "token expired")
    client_id = jwt_parsed["clientId"]
    new_header = MutableHeaders(request._headers)
    new_header["ClientID"] = client_id
    del new_header["Authorization"]
    request._headers = new_header
    yield
