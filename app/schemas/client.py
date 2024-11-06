from datetime import date
from typing import Optional

from fastapi import Form
from pydantic import BaseModel, ConfigDict


class Client(BaseModel):
    """
    Модель данных для создания клиента.

    Атрибуты:
    - mail (str): Электронная почта клиента.
    - password (str): Пароль клиента.
    - name (str): Имя клиента.
    - last_name (str): Фамилия клиента.
    - sex (str): Пол клиента.
    - latitude (float): Широта местоположения клиента.
    - longitude (float): Долгота местоположения клиента.
    """
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
        """
        Метод для передачи параметров через форму в формате FastAPI.
        """
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
    """
    Модель данных для ответа с информацией о клиенте.

    Атрибуты:
    - id (int): Идентификатор клиента.
    - mail (Optional[str]): Электронная почта клиента.
    - sex (Optional[str]): Пол клиента.
    - name (Optional[str]): Имя клиента.
    - last_name (Optional[str]): Фамилия клиента.
    - latitude (Optional[float]): Широта местоположения клиента.
    - longitude (Optional[float]): Долгота местоположения клиента.
    - registration_date (Optional[date]): Дата регистрации клиента.
    - profile_pic (Optional[str]): Путь к изображению профиля клиента.
    """
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
    """
    Модель данных для обновления информации о клиенте.

    Атрибуты:
    - mail (Optional[str]): Новая электронная почта клиента.
    - password (Optional[str]): Новый пароль клиента.
    - name (Optional[str]): Новое имя клиента.
    - last_name (Optional[str]): Новая фамилия клиента.
    - sex (Optional[str]): Новый пол клиента.
    - latitude (Optional[float]): Новая широта местоположения клиента.
    - longitude (Optional[float]): Новая долгота местоположения клиента.
    """
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
    ):
        """
        Метод для передачи параметров через форму в формате FastAPI.
        """
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
    """
    Модель данных для токена аутентификации.

    Атрибуты:
    - access_token (str): Токен доступа.
    - token_type (str): Тип токена.
    """
    access_token: str
    token_type: str
