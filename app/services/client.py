import os
import shutil
import uuid
from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.clients import Client
from schemas import client


def create_client(
    data: client.Client,
    db: Session,
    profile_pic: UploadFile
):
    profile_pic.filename = f"{uuid.uuid4().hex}{profile_pic.filename.lower()}"
    path = os.path.join('static', profile_pic.filename)
    with open(path, 'wb+') as buffer:
        shutil.copyfileobj(profile_pic.file, buffer)
    client = Client(
        name=data.name,
        last_name=data.last_name,
        sex=data.sex,
        mail=data.mail,
        profile_pic=path,
        latitude=data.latitude,
        longitude=data.longitude
    )
    try:
        db.add(client)
        db.commit()
        db.refresh(client)
    except Exception as e:
        print('Ошибка добавления клиента:', e)
        raise e
    return client


def get_client(id: int, db):
    return db.query(Client).filter(Client.id == id).first()


def update(profile_pic: UploadFile, id: int, data: client.Client, db: Session):
    client = db.query(Client).filter(Client.id == id).first()
    if not client:
        return {"error": "Клиент не найден."}
    client.name = data.name
    client.last_name = data.last_name
    client.sex = data.sex
    client.mail = data.mail
    client.latitude = data.latitude
    client.longitude = data.longitude
    if profile_pic:
        profile_pic.filename = (
                            f"{uuid.uuid4().hex}{profile_pic.filename.lower()}"
                        )
        path = os.path.join('static', profile_pic.filename)
        with open(path, 'wb+') as buffer:
            shutil.copyfileobj(profile_pic.file, buffer)
        client.profile_pic = path
    try:
        db.commit()
        db.refresh(client)
    except IntegrityError as e:
        db.rollback()
        print('Ошибка обновления клиента:', e)
        return {"error": "Произошла ошибка при обновлении клиента."}
    return client


def remove(id: int, db: Session):
    client = db.query(Client).filter(Client.id == id).first()
    if not client:
        return {"error": "Клиент не найден."}
    if client.profile_pic and os.path.exists(client.profile_pic):
        os.remove(client.profile_pic)
    db.delete(client)
    db.commit()
    return {"message": "Клиент успешно удален."}
