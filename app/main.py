from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import engine, Base
from routers import client as ClientRouter


Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(ClientRouter.router, prefix="/api")
app.mount("/static", StaticFiles(directory="static"), name="static")
