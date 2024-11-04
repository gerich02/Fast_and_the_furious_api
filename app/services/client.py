from models.clients import Client
from sqlalchemy.orm import Session
from schemas import client

def create_client(data: client.Client, db):
    client = Client(
        name=data.name,
        last_name=data.last_name,
        sex=data.sex,
        mail=data.mail,
        profile_pic=data.profile_pic,
        latitude=data.latitude,
        longitude=data.longitude
    )
    try:
        db.add(client)
        db.commit()
        db.refresh(client)

    except Exception as e:
        print('Ошибка добавления клиента')

    return client

def get_client(id: int, db):
    return db.query(Client).filter(Client.id==id).first()

def update(id:int, data: client.Client, db: Session):
    client = db.query(Client).filter(Client.id==id).first()
    client.name=data.name
    client.last_name=data.last_name
    client.sex=data.sex
    client.mail=data.mail
    client.profile_pic=data.profile_pic
    client.latitude=data.latitude
    client.longitude=data.longitude

    db.add(client)
    db.commit()
    db.refresh(client)

    return client

def remove( id: int, db: Session):
    client = db.query(Client).filter(Client.id==id).delete()
    db.commit()
    return client