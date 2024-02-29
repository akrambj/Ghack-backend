from fastapi import APIRouter, status, Depends
from Models.Requests.AuthRequestsModels import RegisterRequest,LoginRequest
from Core.Shared.Database import Database , db
from Core.Shared.Storage import Storage
from Core.Shared.Security import *
from starlette.responses import JSONResponse
from Core.Shared.ErrorResponses import *
from datetime import datetime
from Middlewares.authProtectionMiddlewares import *
from fastapi import UploadFile
from fastapi import File
from Core.env import TEMP_FILES_DIRECTORY
import os
import uuid
import mimetypes


authRouter = APIRouter()

@authRouter.get("/")
def welcome():
    return "Router working"

@authRouter.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(request: RegisterRequest):
    try:
        data = request.dict()

        result = db.collection("users").where("email", "==", data["email"]).get()

        if len(result) > 0:
            return {
                "success" : False,
                "message" : "Email already exists"
            }
        
        color = data["color"]

        if color < 0 or color > 5:
            return badRequestError("Color should be between 0 and 5")
        
        
        user = {
            "id": str(uuid.uuid4()),
            "firstName": data["firstName"],
            "lastName": data["lastName"],
            "email": data["email"].lower(),
            "password": hashPassword(data["password"]),
            "color": data["color"],
            "imageSrc": "https://storage.googleapis.com/ghack-cf0c2.appspot.com/1709157923Group%201000003516.png",

        }

        Database.store("users", user["id"], user)

        del user["password"]

        jwtToken = createJwtToken({"id":user["id"]})

        del user["id"]

        response = JSONResponse(
                            content={"success":True,"user":user, "token" : jwtToken},
                            headers={"Authorization": f"Bearer {jwtToken}"},
                            )
        
        return response

    except Exception as e:
        return {"success" : False, "message" : str(e)}

@authRouter.post("/updateImage", status_code=status.HTTP_201_CREATED)
async def updateImage(file: UploadFile = File(...), userID: str = Depends(statusProtected)):
    try:
        time = int(datetime.now().timestamp())
        fileID = str(time) + file.filename

        # Store the file to TEMP_FILES_DIRECTORY
        position = TEMP_FILES_DIRECTORY + fileID

        #Check if yje file is an image
        with open(position, "wb") as file_object:
            file_object.write(file.file.read()) 

        # Check if the file is an image
        mime_type, _ = mimetypes.guess_type(file.filename)
        print(mime_type)
        if not mime_type or not mime_type.startswith('image'):
            # Delete the file from TEMP_FILES_DIRECTORY
            os.remove(position)
            return badRequestError("Uploaded file is not an image") 
        


        f = open(position, 'rb')
        # Store the file to the storage
        url = Storage.store(f, fileID)
        f.close()
        # Delete the file from TEMP_FILES_DIRECTORY
        os.remove(position)
        
        user = Database.read("users", userID)
        if user is None:
            return badRequestError("User not found")
        user["image"] = url
        Database.edit("users", userID, user)

        return {"success" : True, "imageSrc" : url}
    except Exception as e:
        return {"success" : False, "message" : str(e)}

@authRouter.post("/login", status_code=status.HTTP_201_CREATED)
async def login_user(request: LoginRequest):
    try:
        data = request.dict()

        result = db.collection("users").where("email", "==", data["email"].lower()).get()

        if len(result) == 0:
            return {
                "success" : False,
                "message" : "Email does not exist"
            }
        user = result[0].to_dict()

        if user["password"] == hashPassword(data["password"]):
            del user["password"]
            
            jwtToken = createJwtToken({"id":user["id"]})

            del user["id"]

            response = JSONResponse(
                            content={"success":True,"user":user, "token" : jwtToken},
                            headers={"Authorization": f"Bearer {jwtToken}"},
                            )

            response.set_cookie(key="Authorization", value=jwtToken,httponly=True)
            return response
        
        return {
            "success" : False,
            "message" : "Invalid credentials"
        }
    except Exception as e:
        return {"success" : False, "message" : str(e)}