from pydantic import BaseModel


class Client(BaseModel):
    mail: str
    password: str
    name: str
    last_name: str
    hashed_password: str
    sex: str
    latitude: float
    longitude: float

    class Config:
        orm_mode = True
        exclude = {"hashed_password"}


class Token(BaseModel):
    access_token: str
    token_type: str
