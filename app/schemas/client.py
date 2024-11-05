from pydantic import BaseModel


class Client(BaseModel):
    mail: str
    password: str
    name: str
    last_name: str
    sex: str
    latitude: float
    longitude: float


class Token(BaseModel):
    access_token: str
    token_type: str
