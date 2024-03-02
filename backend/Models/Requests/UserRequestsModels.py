from pydantic import BaseModel

class EditColorRequest(BaseModel):
    color: int

