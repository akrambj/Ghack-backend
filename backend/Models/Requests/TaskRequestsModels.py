from pydantic import BaseModel
from typing import Optional



class AddTaskRequest(BaseModel):
    name : str
    deadline : str
    assignee : str

class AddPersonalTaskRequest(BaseModel):
    name : str
    deadline : str

class UserUpdateTaskStatusRequest(BaseModel):
    status : str