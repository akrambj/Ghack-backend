from fastapi import APIRouter, status, Depends
from Models.RequestModels import registerRequest
from Core.Shared.Database import Database

authRouter = APIRouter()

@authRouter.get("/")
def welcome():
    return "Router working"

@authRouter.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(request: registerRequest):
    data = request.dict()

    result = Database.store("users", data["email"], data)

    return request.dict()
    