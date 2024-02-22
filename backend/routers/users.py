from fastapi import APIRouter, status, Depends
from .. import schemas, models
from sqlalchemy.orm import Session
from ..hashing import Hash
from .. import database


router = APIRouter(
    tags=['users'],
    prefix="/users"
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(request: schemas.User, db: Session = Depends(database.get_db)):

    new_user = models.User(username=request.username,
                           email=request.email, password=Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
