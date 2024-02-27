from fastapi import APIRouter, status, Depends
from Models.Requests.ProjectRequestsModels import *
from Middlewares.authProtectionMiddlewares import statusProtected
from Routers.tasksRouter import tasksRouter
from Core.Shared.Database import Database , db
from Core.Shared.Storage import *
from Core.Shared.Security import *
from Core.Shared.Utils import *
from Core.env import TEMP_FILES_DIRECTORY
from starlette.responses import JSONResponse
from fastapi import UploadFile
from fastapi import File
import uuid

storageRouter = APIRouter()

@storageRouter.post("/public", status_code=status.HTTP_201_CREATED)
async def storeInPublicStorage(file: UploadFile = File(...), userID: str = Depends(statusProtected)):
    try:
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


        return {"success" : True, "url" : url}
    except Exception as e:
        return {"success" : False, "message" : str(e)}
    
