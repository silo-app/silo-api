from pydantic import BaseModel


class TokenRequest(BaseModel):
    token_name: str
