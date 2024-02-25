from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from Core.env import HASHING_SECRET_KEY, HASH_ALGORITHM
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
        detail={
            "success": False,
            "message": f"Could not validate credentials"},
    )

def statusProtected(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, HASHING_SECRET_KEY, algorithms=[HASH_ALGORITHM])
        print(payload)
        id: str = payload.get("id")
        if id == None:
            raise credentials_exception

        # Else , continue. (Don't raise any exception)
        return id
    except HTTPException as e:
        raise e
    except Exception:
        print("credentials exception")
        raise credentials_exception