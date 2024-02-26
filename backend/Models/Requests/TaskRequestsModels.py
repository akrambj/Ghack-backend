from pydantic import BaseModel
from typing import Optional



class AddTaskRequest(BaseModel):
    name : str
    deadline : str
    assignee : str

class UserUpdateTaskStatusRequest(BaseModel):
    status : str