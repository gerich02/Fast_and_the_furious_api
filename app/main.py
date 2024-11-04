import uvicorn
from fastapi import FastAPI
from database import SessionLocal, engine, Base
from routers import client as ClientRouter
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(ClientRouter.router, prefix='/api')

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', reload=True,workers=3)