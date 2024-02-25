import hashlib
import datetime
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import  HTTPException ,status
from Core.env import HASHING_SECRET_KEY, HASH_ALGORITHM, TOKEN_LIFE_TIME


def hashPassword(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def createJwtToken(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=TOKEN_LIFE_TIME)  # Default expiration time
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, HASHING_SECRET_KEY, algorithm=HASH_ALGORITHM)
    return encoded_jwt

def decodeJwtToken(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, b64decode(HASHING_SECRET_KEY), algorithms=[HASH_ALGORITHM])
        print(payload)
        return payload
    except Exception as e:
        raise credentials_exception