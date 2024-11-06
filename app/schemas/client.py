from datetime import date
from typing import Optional

from fastapi import Form
from pydantic import BaseModel, ConfigDict


class Client(BaseModel):
    mail: str
    password: str
    name: str
    last_name: str
    sex: str
    latitude: float
    longitude: float

    @classmethod
    def as_form(
        cls,
        mail: str = Form(...),
        password: str = Form(...),
        name: str = Form(...),
        last_name: str = Form(...),
        sex: str = Form(...),
        latitude: float = Form(...),
        longitude: float = Form(...),
    ):
        return cls(
            mail=mail,
            password=password,
            name=name,
            last_name=last_name,
            sex=sex,
            latitude=latitude,
            longitude=longitude,
        )


class ClientResponse(BaseModel):
    id: int
    mail: Optional[str] = None
    sex: Optional[str] = None
    name: Optional[str] = None
    last_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    registration_date: Optional[date] = None
    profile_pic: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ClientUpdate(BaseModel):
    mail: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    last_name: Optional[str] = None
    sex: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @classmethod
    def as_form(
        cls,
        mail: Optional[str] = Form(None),
        password: Optional[str] = Form(None),
        name: Optional[str] = Form(None),
        last_name: Optional[str] = Form(None),
        sex: Optional[str] = Form(None),
        latitude: Optional[float] = Form(None),
        longitude: Optional[float] = Form(None),
    ) -> "ClientUpdate":
        return cls(
            mail=mail,
            password=password,
            name=name,
            last_name=last_name,
            sex=sex,
            latitude=latitude,
            longitude=longitude,
        )


class Token(BaseModel):
    access_token: str
    token_type: str
