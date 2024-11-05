from fastapi import (APIRouter, Depends, File, BackgroundTasks,
                     UploadFile, HTTPException)
from sqlalchemy.orm import Session
from typing import Annotated
from database import get_db
from schemas import client as ClientSchemas
from services import client as ClientService
from auth.auth import get_current_user
from starlette import status
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
    current_user: dict = Depends(get_current_user)
):
    client = ClientService.get_client(id, db)
    if client.id != current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Не разрешено обновлять этого клиента"
        )
    return ClientService.update(profile_pic, id, data, db, background_tasks)


@router.delete("/clients/{id}", tags=["Client"])
async def delete(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    client = ClientService.get_client(id, db)
    if client.id != current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Не разрешено удалять этого клиента"
        )
    return ClientService.remove(id, db)
