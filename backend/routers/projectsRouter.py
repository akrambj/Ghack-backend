from fastapi import APIRouter, status, Depends
from Models.RequestModels import *
from Middlewares.authProtectionMiddlewares import statusProtected
from Core.Shared.Database import Database , db
from Core.Shared.Security import *
from starlette.responses import JSONResponse
import uuid


projectsRouter = APIRouter()

@projectsRouter.get("/")
def welcome():
    return "Router working"

@projectsRouter.post("/", status_code=status.HTTP_201_CREATED)
async def get(userID: str = Depends(statusProtected)):
    try:
        print("Not done yet")

    except Exception as e:
        return {"success" : False, "message" : str(e)}

@projectsRouter.post("/create", status_code=status.HTTP_201_CREATED)
async def createProject(request: ProjectCreationRequest,userID: str = Depends(statusProtected)):
    try:
        data = request.dict()
        projetID = str(uuid.uuid4())
        project = {
            "id": projetID,
            "name": data["name"],
            "deadline": data["deadline"],
            "owner": userID,
            "manager": None,
            "members": [userID]
        }

        Database.store("projects", projetID, project)
        return {"success" : True, "message" : "Project created successfully"}
    except Exception as e:
        return {"success" : False, "message" : str(e)}
    
@projectsRouter.get("/status/{projectID}", status_code=status.HTTP_201_CREATED)
async def userStatus(projectID : str,userID: str = Depends(statusProtected)):
    try:
        project = Database.read("projects", projectID)
        if project is None:
            return {"success" : False, "message" : "Project not found"}
        
        if userID == project["owner"]:
            return {"success" : True, "status" : "OWNER"}
        elif userID == project["manager"]:
            return {"success" : True, "status" : "MANAGER"}
        elif userID in project["members"]:
            return {"success" : True, "status" : "EMPLOYEE"}
        return {"success" : False, "message" : "User not found in project"}
    except Exception as e:
        return {"success" : False, "message" : str(e)}