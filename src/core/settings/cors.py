from pydantic import validator

from src.core.settings.base import _BaseModel


class CORSSettings(_BaseModel):

    allow_origins: list[str] = ["*"]
    allow_credentials: bool | None = True
    allow_methods: list[str] = [
        "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD",
    ]
    allow_headers: list[str] = [
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Credentials",
    ]

    @validator(
        'allow_origins',
        'allow_methods',
        'allow_headers',
        pre=True,
    )
    def to_list(cls, value: str | list[str]):
        if isinstance(value, str):
            value = [i.strip() for i in value.strip("[]").split(",")]
        return value
