from pydantic import BaseModel


class Request2FACode(BaseModel):
    user_id: str
    email: str

class Validate2FACode(BaseModel):
    user_id: str
    code: str