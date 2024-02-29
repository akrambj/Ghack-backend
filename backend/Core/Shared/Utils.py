from Core.Shared.Database import Database , db
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi import status
from Core.Shared.ErrorResponses import *
from Core.env import HASHING_SECRET_KEY, HASH_ALGORITHM

def formatUser(id):
    user = db.collection("users").document(id).get().to_dict()
    del user["password"]
    return user

def emailFromId(id):
    return db.collection("users").document(id).get().to_dict()["email"]

def extractStatus(project,userID):
    if project["owner"] == userID:
        return "OWNER"
    elif project["manager"] == userID:
        return "MANAGER"
    else:
        return "EMPLOYEE"

def isDateCorrect(date):
    try:
        datetime.strptime(date, '%d-%m-%Y')
        return True
    except ValueError:
        return False
    

privilege_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={
        "success": False,
        "message": "User not authorized to access this resource"},
)

bad_request_error = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "success": False,
        "message": "Bad request"},
)


def projectProtected(userID, projectID):
    project = Database.read("projects", projectID)
    if project is None:
        raise bad_request_error
    if userID not in project["members"]:
        raise privilege_error
    return project