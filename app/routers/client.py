from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db

from services import client as ClientService
from schemas import client as ClientSchemas

router = APIRouter()

@router.post('/clients/create', tags=['Client'])
async def create(data: ClientSchemas.Client = None, db: Session = Depends(get_db)):
    return ClientService.create_client(data, db)

@router.post('/clients/{id}', tags=['Client'])
async def get(id: int, db: Session = Depends(get_db)):
     return ClientService.get_client(id, db)

@router.put('/clients/{id}', tags=['Client'])
async def update(id: int, data: ClientSchemas.Client = None, db: Session = Depends(get_db)):
     return ClientService.update(id, data, db)

@router.delete('/clients/{id}', tags=['Client'])
async def delete(id: int = None, db: Session = Depends(get_db)):
     return ClientService.remove(id, db)