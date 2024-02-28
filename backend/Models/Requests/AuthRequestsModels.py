from pydantic import BaseModel

class RegisterRequest(BaseModel):
    firstName: str
    lastName: str
    email: str
    password: str
    color : int

class LoginRequest(BaseModel):
    email: str
    password: str