from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from schemas import client as ClientSchemas
from services import client as ClientService


router = APIRouter()


@router.post('/clients/create', tags=['Client'])
async def create(
    data: ClientSchemas.Client = Depends(),
    profile_pic: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return ClientService.create_client(data, db, profile_pic)


@router.get('/clients/{id}', tags=['Client'])
async def get(id: int, db: Session = Depends(get_db)):
    return ClientService.get_client(id, db)


@router.put('/clients/{id}', tags=['Client'])
async def update(
     id: int,
     data: ClientSchemas.Client = Depends(),
     db: Session = Depends(get_db),
     profile_pic: UploadFile = File(...)
):
    return ClientService.update(profile_pic, id, data, db)


@router.delete('/clients/{id}', tags=['Client'])
async def delete(id: int = None, db: Session = Depends(get_db)):
    return ClientService.remove(id, db)
