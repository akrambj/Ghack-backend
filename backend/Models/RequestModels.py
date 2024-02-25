from pydantic import BaseModel

class RegisterRequest(BaseModel):
    firstName: str
    lastName: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ProjectCreationRequest(BaseModel):
    name : str
    deadline : str
    managerEmail : str
    coordinater : bool
    virtualRoom : bool


class AddMemberRequest(BaseModel):
    email : str
    status : str

class deleteMemberRequest(BaseModel):
    email : str