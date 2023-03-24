from pydantic import BaseModel


class _BaseModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True
