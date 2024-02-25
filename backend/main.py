# from .hashing import Hash
from fastapi import FastAPI, Depends, Header
from Routers.authRouter import authRouter
from Routers.projectsRouter import projectsRouter
from Routers.tasksRouter import tasksRouter
from fastapi.middleware.cors import CORSMiddleware
from Middlewares.authProtectionMiddlewares import statusProtected
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
def welcome(user: str = Depends(statusProtected)):
    return user


app.include_router(authRouter, tags=["auth"], prefix="/auth")
app.include_router(projectsRouter, tags=["projects"], prefix="/projects")

# Start the server with the following command:
# uvicorn main:app --reload