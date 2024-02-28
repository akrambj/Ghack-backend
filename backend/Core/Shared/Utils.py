from Core.Shared.Database import Database , db
from datetime import datetime


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
    
