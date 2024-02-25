# from .hashing import Hash
from fastapi import FastAPI
from Routers.authRouter import authRouter
from fastapi.middleware.cors import CORSMiddleware
# Query, Depends, Response, status, HTTPException
#from .models import Base
#from .database import engine, SessionLocal
# from sqlalchemy.orm import Session
#from .routers import users

#Base.metadata.create_all(engine)

app = FastAPI()

# CORS middleware to allow requests from all origins
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get('/')
def welcome():
    return "Welcome to our backend"


app.include_router(authRouter, tags=["auth"], prefix="/auth")

# Start the server with the following command:
# uvicorn main:app --reload