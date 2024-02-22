# from .hashing import Hash
from fastapi import FastAPI
# Query, Depends, Response, status, HTTPException
from .models import Base
from .database import engine, SessionLocal
# from sqlalchemy.orm import Session
from .routers import users
app = FastAPI()


Base.metadata.create_all(engine)
app.include_router(users.router)


@app.get('/')
def welcome():
    return "Welcome to our backend"
