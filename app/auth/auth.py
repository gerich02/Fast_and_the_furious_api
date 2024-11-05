from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from models.clients import Client
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from schemas.client import Token
from database import get_db


router = APIRouter()

SECRET_KEY = 'kFUw7S2U5NCuKOHnSXNH9GJ847JiYgaD24_cvjfYT_4'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='Вы ввели неверные данные'
                    )
    token = create_access_token(user.mail, user.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}


def authenticate_user(mail: str, password: str, db):
    user = db.query(Client).filter(Client.mail == mail).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(mail: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": mail, 'id': user_id}
    expires = datetime.now() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        mail: str = payload.get('sub')
        user_id: int = payload.get('id')
        if mail is None or user_id is None:
            raise HTTPException(
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Пользователь не прошёл проверку'
                            )
        return {'mail': mail, 'id': user_id}
    except JWTError:
        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Пользователь не прошёл проверку'
                        )
