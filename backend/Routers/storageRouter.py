from fastapi import APIRouter, status, Depends
from Models.Requests.ProjectRequestsModels import *
from Middlewares.authProtectionMiddlewares import statusProtected
from Routers.tasksRouter import tasksRouter
from Core.Shared.Database import Database , db
from Core.Shared.Storage import *
from Core.Shared.Security import *
from Core.Shared.Utils import *
from Core.Shared.ErrorResponses import *
from Core.env import TEMP_FILES_DIRECTORY
from starlette.responses import JSONResponse
from fastapi import UploadFile
from fastapi import File
import uuid

storageRouter = APIRouter()

@storageRouter.post("/{state}", status_code=status.HTTP_201_CREATED)
async def storeInPublicStorage(projectID : str,state : str,file: UploadFile = File(...), userID: str = Depends(statusProtected)):
    try:
        
        project = projectProtected(userID, projectID)

        if (state != "public" and state != "private"):
            return badRequestError("State shuld be 'public' or 'private'")
        # Actual timestamp (integer)
        time = int(datetime.now().timestamp())
        fileID = str(time) + file.filename

        # Store the file to TEMP_FILES_DIRECTORY
        position = TEMP_FILES_DIRECTORY + fileID
        with open(position, "wb") as file_object:
            file_object.write(file.file.read())  
        f = open(position, 'rb')
        # Store the file to the storage
        url = Storage.store(f, fileID)
        f.close()
        # Delete the file from TEMP_FILES_DIRECTORY
        os.remove(position)

        file = {
            "name" : file.filename,
            "url" : url,
            "owner" : userID,
            #"description":"FEATURE_IN_DEVELOPMENT"
        }

        # insert the file to the database
        collectionName = "publicCloud" if state == "public" else "privateCloud"
        db.collection("projects").document(projectID).collection(collectionName).document(fileID).set(file)

        return {"success" : True, "url" : url}
    except HTTPException as e:
        raise e 
    except Exception as e:
        return {"success" : False, "message" : str(e)}
    
@storageRouter.get("/{state}", status_code=status.HTTP_201_CREATED)
async def storeInPublicStorage(projectID : str,state : str,userID: str = Depends(statusProtected)):
    try:

        project = projectProtected(userID, projectID)

        if (state != "public" and state != "private"):
            return badRequestError("State shuld be 'public' or 'private'")
        
        collectionName = "publicCloud" if state == "public" else "privateCloud"
        files = db.collection("projects").document(projectID).collection(collectionName).where("owner", "==", userID).get()
        filesList = [file.to_dict() for file in files]

        for file in filesList:
            del file["owner"]
        return {"success" : True, "files" : filesList}
    
    except HTTPException as e:
        raise e 
    except Exception as e:
        return {"success" : False, "message" : str(e)}