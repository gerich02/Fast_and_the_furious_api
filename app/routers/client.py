from fastapi import APIRouter, Depends, File, BackgroundTasks, UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from database import get_db
from schemas import client as ClientSchemas
from services import client as ClientService
from auth.auth import get_current_user
from starlette import status
from datetime import date
from typing import Optional

router = APIRouter()
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/clients/create", tags=["Client"])
async def create(
    data: ClientSchemas.Client = Depends(),
    profile_pic: UploadFile = File(...),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    return ClientService.create_client(data, db, profile_pic, background_tasks)


@router.get("/clients/{id}", tags=["Client"])
async def get(id: int, db: Session = Depends(get_db)):
    return ClientService.get_client(id, db)


@router.put("/clients/{id}", tags=["Client"])
async def update(
    id: int,
    data: ClientSchemas.Client = Depends(),
    db: Session = Depends(get_db),
    profile_pic: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: dict = Depends(get_current_user),
):
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
    client = ClientService.get_client(id, db)
    if client.id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Не разрешено удалять этого клиента",
        )
    return ClientService.remove(id, db)


@router.post("/clients/{id}/match", tags=["Match"])
async def match(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
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


@router.get("/clients", tags=["Client"])
def get_clients(
    db: Session = Depends(get_db),
    sex: Optional[str] = None,
    name: Optional[str] = None,
    last_name: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    sort_by: Optional[str] = None,
):
    return ClientService.get_all_clients(
        db, sex, name, last_name, start_date, end_date, sort_by
    )
