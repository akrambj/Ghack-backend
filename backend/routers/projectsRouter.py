from fastapi import APIRouter, status, Depends
from Models.RequestModels import *
from Middlewares.authProtectionMiddlewares import statusProtected
from Core.Shared.Database import Database , db
from Core.Shared.Security import *
from Core.Shared.Utils import *
from starlette.responses import JSONResponse
import uuid


projectsRouter = APIRouter()

@projectsRouter.get("/", status_code=status.HTTP_201_CREATED)
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

@projectsRouter.get("/{projectID}", status_code=status.HTTP_201_CREATED)
async def getSingleProject(projectID : str,userID: str = Depends(statusProtected)):
    try:
        project = Database.read("projects", projectID)
        if project is None:
            return {"success" : False, "message" : "Project not found"}
        
        project["status"] = extractStatus(project,userID)

        # Get members information
        members = []
        for member in project["members"]:
            members.append(formatUser(member))
        project["members"] = members
        
        return {"success" : True, "project" : project}

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
            "manager": data["managerEmail"],
            "members": [userID],
            "virtualRoom": data["virtualRoom"],
            "coordinater": data["coordinater"]
        }

        Database.store("projects", projetID, project)

        return {"success" : True, "message" : "Project created successfully"}
    except Exception as e:
        return {"success" : False, "message" : str(e)}

@projectsRouter.post("/members/{projectID}", status_code=status.HTTP_201_CREATED)
async def addMember(projectID: str,request: AddMemberRequest ,userID: str = Depends(statusProtected)):
    try:
        data = request.dict()
        user = db.collection("users").where("email", "==", data["email"].lower()).get()
        if len(user) == 0:
            return {"success" : False, "message" : "User not found"}
        user = user[0].to_dict()
        userID = user["id"]
        project = Database.read("projects", projectID)
        if project is None:
            return {"success" : False, "message" : "Project not found"}
        if userID in project["members"]:
            project["members"].remove(userID)

        project["members"].append(userID)
        if data["status"] == "MANAGER":
            project["manager"] = userID
        Database.store("projects", projectID, project)
        return {"success" : True, "message" : "User added to project"}
    
    except Exception as e:
        return {"success" : False, "message" : str(e)}

@projectsRouter.delete("/{projectID}", status_code=status.HTTP_201_CREATED)
async def createProject(projectID : str,userID: str = Depends(statusProtected)):
    try:
        project = Database.read("projects", projectID)
        if project is None:
            return {"success" : False, "message" : "Project not found"}

        if userID == project["owner"]:
            Database.delete("projects", projectID)
            return {"success" : True, "message" : "Project deleted successfully"}
        else:
            return {"success" : False, "message" : "User not authorized to delete project"}
    
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
    
@projectsRouter.delete("/members/{projectID}", status_code=status.HTTP_201_CREATED)
async def removeMember(projectID: str,request: deleteMemberRequest ,userID: str = Depends(statusProtected)):
    try:
        data = request.dict()
        user = db.collection("users").where("email", "==", data["email"].lower()).get()
        if len(user) == 0:
            return {"success" : False, "message" : "User not found"}
        user = user[0].to_dict()
        userID = user["id"]
        project = Database.read("projects", projectID)
        if project is None:
            return {"success" : False, "message" : "Project not found"}
        if userID in project["members"]:
            if userID == project["owner"]:
                return {"success" : False, "message" : "Owner cannot be removed from project"}
            elif userID == project["manager"]:
                project["manager"] = None
            project["members"].remove(userID)
        Database.store("projects", projectID, project)
        return {"success" : True, "message" : "User removed from project"}
    
    except Exception as e:
        return {"success" : False, "message" : str(e)}