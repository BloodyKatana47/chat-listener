from pydantic import BaseModel


class Account(BaseModel):
    api_hash: str
    api_id: int
    session_name: str
