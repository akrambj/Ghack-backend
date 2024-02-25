from fastapi import APIRouter, status, Depends
from Models.RequestModels import RegisterRequest,LoginRequest
from Core.Shared.Database import Database , db
from Core.Shared.Security import *
from starlette.responses import JSONResponse
import uuid


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
        
        
        user = {
            "id": str(uuid.uuid4()),
            "firstName": data["firstName"],
            "lastName": data["lastName"],
            "email": data["email"].lower(),
            "password": hashPassword(data["password"])
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