from Core.Shared.Database import Database , db
from datetime import datetime


def formatUser(id):
    user = db.collection("users").document(id).get().to_dict()
    del user["password"]
    return user

def extractStatus(project,userID):
    if project["owner"] == userID:
        project["status"] = "OWNER"
    elif project["manager"] == userID:
        project["status"] = "MANAGER"
    else:
        project["status"] = "EMPLOYEE"

def isDateCorrect(date):
    try:
        datetime.strptime(date, '%d-%m-%Y')
        return True
    except ValueError:
        return False
    
