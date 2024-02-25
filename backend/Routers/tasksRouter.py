from fastapi import APIRouter, status, Depends
from Models.RequestModels import *
from Middlewares.authProtectionMiddlewares import statusProtected
from Core.Shared.Database import Database , db
from Core.Shared.Security import *
from Core.Shared.Utils import *
from starlette.responses import JSONResponse
import uuid


tasksRouter = APIRouter()

@tasksRouter.get("/", status_code=status.HTTP_201_CREATED)
async def get(userID: str = Depends(statusProtected)):
    
    try:
        # Get all the projects a user is part of
        projects = db.collection("projects").where("members", "array_contains", userID).get()
        projects = [project.to_dict() for project in projects]
    
        for project in projects:
            project["status"] = extractStatus(project,userID)
            

            # Get members information
            members = []
            for member in project["members"]:
                members.append(formatUser(member))
            project["members"] = members


        return {"success" : True, "projects" : projects}

    except Exception as e:
        return {"success" : False, "message" : str(e)}