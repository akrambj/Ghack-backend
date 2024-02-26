from pydantic import BaseModel

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