from typing import List, Union

from pydantic import BaseModel, Field


class HelloSchema(BaseModel):
    message: str = Field(...)


class Endpoint(BaseModel):
    url: str
    protected: bool
    methods: List[str]


class Service(BaseModel):
    name: str
    port: str
    ip: str
    label: str
    endpoints: Union[List[Endpoint], None]
