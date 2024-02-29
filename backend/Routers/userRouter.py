from fastapi import APIRouter, status, Depends
from Models.Requests.ProjectRequestsModels import *
from Middlewares.authProtectionMiddlewares import statusProtected
from Routers.tasksRouter import tasksRouter
from Routers.storageRouter import storageRouter
from Core.Shared.ErrorResponses import *
from Core.Shared.Database import Database , db
from Core.Shared.Security import *
from Core.Shared.Utils import *
from starlette.responses import JSONResponse
import uuid



userRouter = APIRouter()


@userRouter.get("/profile", status_code=status.HTTP_201_CREATED)
async def getProfile(userID: str = Depends(statusProtected)):
    try:
        user = Database.read("users", userID)
        if user is None:
            return badRequestError("User not found")
        del user["password"]
        return {"success" : True, "user" : user}

    except Exception as e:
        return {"success" : False, "message" : str(e)}

@userRouter.put("/profile", status_code=status.HTTP_201_CREATED)
async def editProfile(request : dict,userID: str = Depends(statusProtected)):
    try:
        data = request
        user = {}
        if "firstName" in data:
            user["firstName"] = data["firstName"]
        if "lastName" in data:
            user["lastName"] = data["lastName"]
        if "email" in data:
            user["email"] = data["email"]
        if "password" in data:
            user["password"] = hashPassword(data["password"])
        
        if len(user) == 0:
            return badRequestError("No data to update")
        
        
        Database.edit("users", userID, user)
        return {"success" : True, "user" : user }

    except Exception as e:
        return {"success" : False, "message" : str(e)}
    
@userRouter.get("/invitations", status_code=status.HTTP_200_OK)
async def getInvitations(userID: str = Depends(statusProtected)):
    try:
        invitations = db.collection("users").document(userID).collection("invitations").get()
        invitations = [invitation.to_dict() for invitation in invitations]
        return {"success" : True, "invitations" : invitations}
    except Exception as e:
        return {"success" : False, "message" : str(e)}
    
@userRouter.post("/invitations/{invitationID}", status_code=status.HTTP_201_CREATED)
async def acceptInvitation(invitationID: str,userID: str = Depends(statusProtected)):
    try:
        invitation = db.collection("users").document(userID).collection("invitations").document(invitationID).get()
        invitation = invitation.to_dict()

        if invitation is None:
            return badRequestError("Invitation not found")
        if invitation["destination"] != userID:
            return privilegeError("User not authorized to accept this invitation")

        projectID = invitation["projectID"]
        project = Database.read("projects", projectID)
        project["members"].append(userID)
        if invitation["status"] == "MANAGER":
            project["manager"] = userID
        Database.store("projects", projectID, project)
        return {"success" : True, "message" : "User added to project"}
    
    except Exception as e:
        return {"success" : False, "message" : str(e)}
    
@userRouter.delete("/invitations/{invitationID}", status_code=status.HTTP_200_OK)
async def declineInvitation(invitationID: str,userID: str = Depends(statusProtected)):
    try:
        if not db.collection("users").document(userID).collection("invitations").document(invitationID).get().exists:
            return badRequestError("Invitation not found")

        db.collection("users").document(userID).collection("invitations").document(invitationID).delete()
        return {"success" : True, "message" : "Invitation declined"}
    except Exception as e:
        return {"success" : False, "message" : str(e)}