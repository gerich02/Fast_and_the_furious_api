from pydantic import BaseModel

class Client(BaseModel):

    name : str
    last_name: str
    sex: str
    mail: str
    profile_pic: str
    latitude: float
    longitude: float