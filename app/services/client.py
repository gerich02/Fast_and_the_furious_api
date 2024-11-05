import os
import shutil
import uuid
from fastapi import UploadFile, BackgroundTasks
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.clients import Client
from schemas import client
from PIL import Image


def add_watermark(image_path: str, watermark_path: str):
    original_image = Image.open(image_path)
    watermark = Image.open(watermark_path)
    if original_image.mode == 'RGBA':
        original_image = original_image.convert('RGB')
    original_image.paste(watermark, (0, 0), watermark)
    original_image.save(image_path, format='JPEG')


def create_client(
    data: client.Client,
    db: Session,
    profile_pic: UploadFile,
    background_tasks: BackgroundTasks,
):
    profile_pic.filename = f"{uuid.uuid4().hex}_{profile_pic.filename.lower()}"
    path = os.path.join("static", profile_pic.filename)
    with open(path, "wb+") as buffer:
        shutil.copyfileobj(profile_pic.file, buffer)
    background_tasks.add_task(add_watermark, path, "static/watermark.png")
    client = Client(
        name=data.name,
        last_name=data.last_name,
        sex=data.sex,
        mail=data.mail,
        profile_pic=path,
        latitude=data.latitude,
        longitude=data.longitude,
    )
    try:
        db.add(client)
        db.commit()
        db.refresh(client)
    except Exception as e:
        print("Ошибка добавления клиента:", e)
        raise e
    return client


def get_client(id: int, db):
    return db.query(Client).filter(Client.id == id).first()


def update(
    profile_pic: UploadFile,
    id: int,
    data: client.Client,
    db: Session,
    background_tasks: BackgroundTasks,
):
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
        if os.path.exists(client.profile_pic):
            os.remove(client.profile_pic)
        profile_pic.filename = (
            f"{uuid.uuid4().hex}"
            f"{profile_pic.filename.lower()}"
        )
        path = os.path.join("static", profile_pic.filename)
        try:
            with open(path, "wb+") as buffer:
                shutil.copyfileobj(profile_pic.file, buffer)
            background_tasks.add_task(
                add_watermark,
                path,
                "static/watermark.png"
            )
            client.profile_pic = path
        except Exception as e:
            print("Ошибка при сохранении профиля:", e)
            return {"error": "Не удалось сохранить изображение профиля."}
    try:
        db.commit()
        db.refresh(client)
    except IntegrityError as e:
        db.rollback()
        print("Ошибка обновления клиента:", e)
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
