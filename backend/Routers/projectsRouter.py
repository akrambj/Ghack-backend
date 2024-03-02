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
from services import indexing
import uuid
from livekit import api
from fastapi import status


projectsRouter = APIRouter()

@projectsRouter.get("/statistics/{projectID}", status_code=status.HTTP_200_OK)
async def getStatistics(projectID: str, userID: str = Depends(statusProtected)):
    #try:
        project = projectProtected(userID, projectID)
        if project["owner"] != userID:
            return privilegeError("User not authorized to view statistics")
        tasks = db.collection("projects").document(projectID).collection("tasks").get()
        tasks = [task.to_dict() for task in tasks]
        numberTasks = len(tasks)
        numberParticipants = len(project["members"])
        publicFiles = db.collection("projects").document(projectID).collection("publicCloud").get()
        numberFilesPublic = len(publicFiles)
        privateFiles = db.collection("projects").document(projectID).collection("privateCloud").get()
        numberFilesPrivate = len(privateFiles)
        totalFiles = numberFilesPublic + numberFilesPrivate

        members = project["members"]
        print(members)
        # Extract the status , number of tasks and number of files from each member
        updatedMembers = []
        for member in members:
            # Extarct number of tasks done by member
            member = db.collection("users").document(member).get().to_dict()
            del member["password"]
            member["email"] = emailFromId(member["id"])
            memberTasks = db.collection("projects").document(projectID).collection("tasks").where("assignee", "==", member).where("status", "==", "DONE").get()
            member["nbTasks"] = len(memberTasks)
            # Extract number of files uploaded by member
            memberPublicFiles = db.collection("projects").document(projectID).collection("publicCloud").where("owner",
                                                                                                              "==",
                                                                                                              member).get()
            memberPrivateFiles = db.collection("projects").document(projectID).collection("privateCloud").where("owner",
                                                                                                                "==",
                                                                                                                member).get()
            member["nbTotalFiles"] = len(memberPublicFiles) + len(memberPrivateFiles)
            if member["id"] == project["manager"]:
                member["status"] = "MANAGER"
            elif member["id"] == project["owner"]:
                member["status"] = "OWNER"
            else:
                member["status"] = "EMPLOYEE"

            updatedMembers.append(member)

        return {"success": True,
                "statistics": {"tasks": numberTasks, "participants": numberParticipants, "files": totalFiles,
                               "members": updatedMembers}}

@projectsRouter.get("/files", status_code=status.HTTP_200_OK)
async def search_files(search: str | None = None, userId :str = Depends(statusProtected)):
  try:
    index_name = "file_key_words"

    if search:
        return {"file_urls": indexing.search_documents(index_name, search)}
    return badRequestError("no query has been provided!")

  except Exception as e:
        return {"success": False, "message": str(e)}

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

            del project['manager']
            del project['owner']


        return {"success" : True, "projects" : projects}

    except Exception as e:
        return {"success" : False, "message" : str(e)}



@projectsRouter.get("/{projectID}", status_code=status.HTTP_201_CREATED)
async def getSingleProject(projectID : str,userID: str = Depends(statusProtected)):
    try:

        project = projectProtected(userID, projectID)
        
        project["status"] = extractStatus(project,userID)

        # Get members information
        members = []
        for member in project["members"]:
            formattedUser = formatUser(member)
            del formattedUser["id"]
            members.append(formattedUser)
        project["members"] = members

        managerMail = emailFromId(project["manager"])
        ownerMail = emailFromId(project["owner"])

        project["manager"] = managerMail
        project["owner"] = ownerMail
        
        return {"success" : True, "project" : project}
    except HTTPException as e:
        raise e 
    except Exception as e:
        return {"success" : False, "message" : str(e)}

@projectsRouter.post("/create", status_code=status.HTTP_201_CREATED)
async def createProject(request: ProjectCreationRequest,userID: str = Depends(statusProtected)):
    try:
        data = request.dict()
        if not isDateCorrect(data["deadline"]):
            raise Exception("Invalid date format")
        projetID = str(uuid.uuid4())
        data["id"] = projetID
        data["status"] = "OWNER"
        managerID = db.collection("users").where("email", "==", data["managerEmail"].lower()).get()
        if len(managerID) == 0:
            return badRequestError("Manager not found")
        managerID = managerID[0].to_dict()["id"]

        if managerID == userID:
            return badRequestError("User cannot be manager of his own project")

        project = {
            "id": projetID,
            "name": data["name"],
            "deadline": data["deadline"],
            "owner": userID,
            "manager": managerID,
            "members": [userID,managerID],
            "virtualRoom": data["virtualRoom"],
            "coordinater": data["coordinater"]
        }


        Database.store("projects", projetID, project)

        ownerMail = emailFromId(userID)

        project["members"] = [ownerMail]
        project["owner"] = ownerMail
        project["manager"] = data["managerEmail"]

        return {"success" : True, "message" : "Project created successfully","project":data}
    except Exception as e:
        return {"success" : False, "message" : str(e)}

@projectsRouter.post("/members/{projectID}", status_code=status.HTTP_201_CREATED)
async def addMember(projectID: str,request: AddMemberRequest ,userID: str = Depends(statusProtected)):
    try:
        data = request.dict()
        user = db.collection("users").where("email", "==", data["email"].lower()).get()
        if len(user) == 0:
            return badRequestError("User not found")
        user = user[0].to_dict()
        userID = user["id"]
        project = Database.read("projects", projectID)
        if userID in project["members"]:
            return badRequestError("User already in project")
        if project is None:
            return badRequestError("Project not found")

        # Create an invitation
        invitationID = projectID
        projectMembersId = project["members"]
        projectMembers = []
        for member in projectMembersId:
            projectMembers.append(emailFromId(member))

        invitation = {
            'invitationID': invitationID,
            'projectName' : project["name"],
            'projectID' : projectID,
            'status':data["status"],
            'deadline':project["deadline"],
            'members':projectMembers,
            'destination':userID
            }
        
        db.collection("users").document(userID).collection("invitations").document(invitationID).set(invitation)
        return {"success" : True, "message" : "Invitation sent successfully"}



    
    except Exception as e:
        return {"success" : False, "message" : str(e)}

@projectsRouter.delete("/{projectID}", status_code=status.HTTP_200_OK)
async def deleteProject(projectID : str,userID: str = Depends(statusProtected)):
    try:
        project = projectProtected(userID, projectID)

        if userID == project["owner"]:
            Database.delete("projects", projectID)
            return {"success" : True, "message" : "Project deleted successfully"}
        else:
            return {"success" : False, "message" : "User not authorized to delete project"}
    except HTTPException as e:
        raise e 
    except Exception as e:
        return {"success" : False, "message" : str(e)}
    
@projectsRouter.get("/status/{projectID}", status_code=status.HTTP_200_OK)
async def userStatus(projectID : str,userID: str = Depends(statusProtected)):
    try:
        
        project = projectProtected(userID, projectID)

        
        if userID == project["owner"]:
            return {"success" : True, "status" : "OWNER"}
        elif userID == project["manager"]:
            return {"success" : True, "status" : "MANAGER"}
        elif userID in project["members"]:
            return {"success" : True, "status" : "EMPLOYEE"}
        return {"success" : False, "message" : "User not found in project"}
    except HTTPException as e:
        raise e 
    except Exception as e:
        return {"success" : False, "message" : str(e)}
    
@projectsRouter.delete("/members/{projectID}", status_code=status.HTTP_200_OK)
async def removeMember(projectID: str,request: deleteMemberRequest ,userID: str = Depends(statusProtected)):
    try:
        
        project = projectProtected(userID, projectID)

        
        if project["owner"] != userID and project["manager"] != userID:
            return privilegeError("User not authorized to remove members")
        

        data = request.dict()
        user = db.collection("users").where("email", "==", data["email"].lower()).get()
        if len(user) == 0:
            return {"success" : False, "message" : "User not found"}
        user = user[0].to_dict()
        userID = user["id"]

        if userID in project["members"]:
            if userID == project["owner"]:
                return badRequestError("Owner cannot be removed from project")
            elif userID == project["manager"]:
                project["manager"] = None
            project["members"].remove(userID)
        Database.store("projects", projectID, project)
        return {"success" : True, "message" : "User removed from project"}
    except HTTPException as e:
        raise e 
    except Exception as e:
        return {"success" : False, "message" : str(e)}


    






@projectsRouter.get("/{projectID}/chatrooms", status_code=status.HTTP_200_OK)
async def getChatrooms(projectID : str,userID: str = Depends(statusProtected) ):
    try:

        user = Database.read("users", userID)
        
        username = user["lastName"]+" "+user["firstName"]

        chatRooms = {
            "privateReunion1" : projectID+"privateReunion1",
            "privateReunion2" : projectID+"privateReunion2",
            "directionRoom" :projectID+"directionRoom",
            "restSpace" : projectID+"restSpace",
            "workSpace" : projectID+"workSpace",
            "meetingRoom" : projectID+"meetingRoom"
        }

        for key in chatRooms:
            chatRooms[key] = generateChatroomToken(username,username,chatRooms[key])
        
        return {"success" : True, "chatroomsTokens" : chatRooms}



    except Exception as e:
        return {"success": False, "message": str(e)}








projectsRouter.include_router(tasksRouter, prefix="/{projectID}/tasks", tags=["tasks"])
projectsRouter.include_router(storageRouter, prefix="/{projectID}/storage", tags=["storage"])