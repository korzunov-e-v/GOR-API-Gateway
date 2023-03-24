import typing

from pydantic import Field
from uvicorn.config import (
    HTTPProtocolType,
    LoopSetupType,
)

from src.core.settings.base import _BaseModel


class UvicornSettings(_BaseModel):
    """Uvicorn Settings"""

    app: str = "main:app"
    host: str = Field("0.0.0.0", description="Bind socket to this host.")
    port: int = Field(8000, description="Bind socket to this port.")
    loop: LoopSetupType = "auto"
    http: HTTPProtocolType = "auto"
    reload: bool = Field(None, description="Enable auto-reload.")
    workers: typing.Optional[int] = None
