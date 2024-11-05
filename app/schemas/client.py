from pydantic import BaseModel


class Client(BaseModel):
    name: str
    last_name: str
    sex: str
    mail: str
    latitude: float
    longitude: float
