import math
import os
import shutil
import uuid
from datetime import date
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import BackgroundTasks, HTTPException, UploadFile
from models.clients import Client, Match
from passlib.context import CryptContext
from PIL import Image
from schemas import client as ClientSchemas
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

load_dotenv()


LIMIT_PER_DAY = int(os.getenv("LIMIT_PER_DAY"))

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def add_watermark(image_path: str, watermark_path: str):
    """
    Добавляет водяной знак к изображению.
    """
    original_image = Image.open(image_path)
    watermark = Image.open(watermark_path)
    if original_image.mode == "RGBA":
        original_image = original_image.convert("RGB")
    original_image.paste(watermark, (0, 0), watermark)
    original_image.save(image_path, format="JPEG")


def create_client(
    data: ClientSchemas.Client,
    db: Session,
    profile_pic: UploadFile,
    background_tasks: BackgroundTasks,
):
    """
    Создаёт нового клиента и добавляет водяной знак к фото профиля.
    """
    profile_pic.filename = f"{uuid.uuid4().hex}_{profile_pic.filename.lower()}"
    path = os.path.join("static", profile_pic.filename)
    with open(path, "wb+") as buffer:
        shutil.copyfileobj(profile_pic.file, buffer)
    background_tasks.add_task(add_watermark, path, "static/watermark.png")
    client = Client(
        mail=data.mail,
        hashed_password=bcrypt_context.hash(data.password),
        name=data.name,
        last_name=data.last_name,
        sex=data.sex,
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
    return ClientSchemas.ClientResponse.model_validate(client)


def get_client(id: int, db):
    """
    Получает клиента по ID.
    """
    client = db.query(Client).filter(Client.id == id).first()
    if client is None:
        raise HTTPException(
            status_code=404, detail=f"Клиент с id {id} не найден в системе"
        )
    return ClientSchemas.ClientResponse.model_validate(client)


@lru_cache(maxsize=1000)
def great_circle_distance(lat1, lon1, lat2, lon2):
    """
    Вычисляет расстояние между двумя точками по их координатам.

    Параметры:
    - lat1, lon1 (float): Широта и долгота первой точки.
    - lat2, lon2 (float): Широта и долгота второй точки.
    """
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad)
        * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    R = 6371.0
    distance = R * c
    return distance


def get_all_clients(
    db,
    sex: str = None,
    name: str = None,
    last_name: str = None,
    start_date: date = None,
    end_date: date = None,
    distance: int = None,
    longitude: float = None,
    latitude: float = None,
    sort_by: str = None,
):
    """
    Получает всех клиентов с возможностью фильтрации и сортировки.
    """
    query = db.query(Client)
    if sex:
        query = query.filter(Client.sex == sex)
    if name:
        query = query.filter(Client.name.ilike(f"%{name}%"))
    if last_name:
        query = query.filter(Client.last_name.ilike(f"%{last_name}%"))
    if start_date:
        query = query.filter(Client.registration_date >= start_date)
    if end_date:
        query = query.filter(Client.registration_date <= end_date)
    if sort_by == "registration_date":
        query = query.order_by(Client.registration_date)
    if distance is not None and longitude is not None and latitude is not None:
        filtered_clients = []
        for user in query:
            if (
                great_circle_distance(
                    latitude, longitude, user.latitude, user.longitude
                )
                < distance
            ):
                filtered_clients.append(
                    ClientSchemas.ClientResponse.model_validate(user)
                )
        return filtered_clients
    return [
        ClientSchemas.ClientResponse.model_validate(client)
        for client in query.all()
    ]


def update(
    profile_pic: UploadFile,
    id: int,
    data: ClientSchemas.ClientUpdate,
    db: Session,
    background_tasks: BackgroundTasks,
):
    """
    Обновляет информацию о клиенте, включая изображение профиля.
    """
    client = db.query(Client).filter(Client.id == id).first()
    if not client:
        return {"error": "Клиент не найден."}
    if data.mail != "":
        client.mail = data.mail
    if data.password != "":
        client.hashed_password = bcrypt_context.hash(data.password)
    if data.name != "":
        client.name = data.name
    if data.last_name != "":
        client.last_name = data.last_name
    if data.sex != "":
        client.sex = data.sex
    if data.latitude != 0:
        client.latitude = data.latitude
    if data.longitude != 0:
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
    return ClientSchemas.ClientResponse.model_validate(client)


def remove(id: int, db: Session):
    """
    Удаляет клиента и его фото профиля.
    """
    client = db.query(Client).filter(Client.id == id).first()
    if not client:
        return {"error": "Клиент не найден."}
    if client.profile_pic and os.path.exists(client.profile_pic):
        os.remove(client.profile_pic)
    db.delete(client)
    db.commit()
    return {"message": "Клиент успешно удален."}


def send_email_mock(subject: str, body: str, recipient: str):
    """
    Имитирует отправку электронного письма.
    """
    print(f"Отправка письма на {recipient}")
    print(f"Тема: {subject}")
    print(f"Сообщение: {body}")
    print("-" * 50)


def matching(matcher_id: int, matched_id: int, db: Session):
    """
    Обрабатывает голосование за симпатию и проверяет наличие взаимности.
    """
    today = date.today()
    match_today = (
        db.query(Match).filter(
            Match.matcher == matcher_id,
            Match.date == today).count()
        )
    if match_today >= LIMIT_PER_DAY:
        return {
            "message": (
                f"Вы достигли лимита на"
                f"{LIMIT_PER_DAY} оценок в день."
            )
        }
    matcher_match = (
        db.query(Match)
        .filter(and_(Match.matcher == matcher_id, Match.matched == matched_id))
        .first()
    )
    matched_match = (
        db.query(Match)
        .filter(and_(Match.matcher == matched_id, Match.matched == matcher_id))
        .first()
    )
    if matcher_match:
        return {"message": "Вы уже голосовали за этого человека."}
    elif not matcher_match and not matched_match:
        matcher_match = Match(matcher=matcher_id, matched=matched_id)
        db.add(matcher_match)
        db.commit()
        db.refresh(matcher_match)
        return {"message": "Вы проголосовали!"}
    else:
        matcher_match = Match(matcher=matcher_id, matched=matched_id)
        db.add(matcher_match)
        db.commit()
        db.refresh(matcher_match)
        matcher_user = db.query(Client).filter(Client.id == matcher_id).first()
        matched_user = db.query(Client).filter(Client.id == matched_id).first()
        subject = "Взаимная симпатия!"
        body_matcher = (
            f"Вы понравились {matched_user.name}!"
            f"  Почта участника: {matched_user.mail}"
        )
        send_email_mock(subject, body_matcher, matcher_user.mail)
        body_matched = (
            f"Вы понравились {matcher_user.name}!"
            f" Почта участника: {matcher_user.mail}"
        )
        send_email_mock(subject, body_matched, matched_user.mail)
        return {
            "message": (
                f"Взаимная симпатия! "
                f"Почта участника: {matched_user.mail}"
            )
        }
