from pydantic import BaseModel


class PVEInfo(BaseModel):
    release: str
    version: str
    repoid: str
