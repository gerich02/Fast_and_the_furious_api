from datetime import date
from typing import Annotated, Optional, Union

from auth.auth import get_current_user
from database import get_db
from fastapi import (APIRouter, BackgroundTasks, Depends, File, HTTPException,
                     UploadFile)
from schemas import client as ClientSchemas
from services import client as ClientService
from sqlalchemy.orm import Session
from starlette import status

router = APIRouter()
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/clients/create", tags=["Client"])
async def create(
    data: ClientSchemas.Client = Depends(ClientSchemas.Client.as_form),
    profile_pic: UploadFile = File(...),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Создает нового клиента.

    **Тело запроса**:
    - `data`: Данные клиента (имя, фамилия, почта, и т. д.)
    - `profile_pic`: Файл изображения профиля клиента
    """
    return ClientService.create_client(data, db, profile_pic, background_tasks)


@router.get("/clients/{id}", tags=["Client"])
async def get(id: int, db: Session = Depends(get_db)):
    """
    Получить информацию о клиенте по ID.
    """
    return ClientService.get_client(id, db)


@router.put("/clients/{id}", tags=["Client"])
async def update(
    id: int,
    data: ClientSchemas.ClientUpdate = Depends(
        ClientSchemas.ClientUpdate.as_form
    ),
    profile_pic: Optional[Union[UploadFile, str]] = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Обновить данные клиента.
    **Тело запроса**:
    - `data`: Новые данные клиента (имя, фамилия и т. д.)
    - `profile_pic`: (Опционально) Новый файл изображения профиля
    """
    client = ClientService.get_client(id, db)
    if client.id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Не разрешено обновлять этого клиента",
        )
    return ClientService.update(profile_pic, id, data, db, background_tasks)


@router.delete("/clients/{id}", tags=["Client"])
async def delete(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Удалить клиента.
    """
    client = ClientService.get_client(id, db)
    if client.id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Не разрешено удалять этого клиента",
        )
    return ClientService.remove(id, db)


@router.get("/clients", tags=["Client"])
def get_clients(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    sex: Optional[str] = None,
    name: Optional[str] = None,
    last_name: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    distance: Optional[int] = None,
    sort_by: Optional[str] = None,
):
    """
    Получить список клиентов.

    **Параметры**:
    - `sex`: Пол клиента (опционально)
    - `name`: Имя клиента (опционально)
    - `last_name`: Фамилия клиента (опционально)
    - `start_date`, `end_date`: Фильтр по дате регистрации
    - `distance`: Фильтр поиска по расстоянию до клиента
    - `sort_by`: Параметр для сортировки списка клиентов
    """
    longitude, latitude = None, None
    if current_user and distance is not None:
        user = ClientService.get_client(current_user["id"], db)
        longitude = user.longitude
        latitude = user.latitude

    return ClientService.get_all_clients(
        db,
        sex,
        name,
        last_name,
        start_date,
        end_date,
        distance,
        longitude,
        latitude,
        sort_by,
    )


@router.post("/clients/{id}/match", tags=["Match"])
async def match(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Оценить другого клиента.

    **Тело запроса**:
    - `id`: ID клиента, которого оценивает текущий пользователь
    """
    matched = ClientService.get_client(id, db)
    matcher = current_user
    if not matcher:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Авторизируйтесь, чтобы голосовать!",
        )
    if matcher["id"] == matched.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Запрещено голосовать за самого себя!",
        )
    return ClientService.matching(matcher["id"], matched.id, db)
