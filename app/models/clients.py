from sqlalchemy import Column, Float, Integer, String

from database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    mail = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String)
    name = Column(String, index=True)
    last_name = Column(String, index=True)
    sex = Column(String, nullable=False, index=True)
    profile_pic = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
