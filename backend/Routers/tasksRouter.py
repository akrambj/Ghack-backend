from fastapi import APIRouter, status, Depends
from Models.Requests.TaskRequestsModels import *
from Middlewares.authProtectionMiddlewares import statusProtected
from Core.Shared.Database import Database , db
from Core.Shared.Security import *
from Core.Shared.Utils import *
from Core.Shared.TaskState import *
from Core.Shared.ErrorResponses import *
from starlette.responses import JSONResponse
import uuid


tasksRouter = APIRouter()

@tasksRouter.post("/add", status_code=status.HTTP_201_CREATED)
async def addTask(projectID: str,request : AddTaskRequest,userID: str = Depends(statusProtected)):
    try:
        # Check if the user is the manager of the project
        project = Database.read("projects", projectID)
        if project is None:
            return badRequestError("Project not found")
        
        if project["manager"] != userID:
            return privilegeError("Only the manager can add tasks")

        # Add the task
        task = request.dict()

        if not isDateCorrect(task["deadline"]):
            return badRequestError("Invalid date format")
        taskID = str(uuid.uuid4())
        task["id"] = taskID
        task["status"] = TaskState.NEW
        assigneeEmail = task["assignee"].lower()
        assignee = db.collection("users").where("email", "==", assigneeEmail).get()
        if len(assignee) == 0:
            raise Exception("Assignee not found")
        task["assignee"] = assignee[0].id
        # Create / Add a new task to the tasks collection
        db.collection("projects").document(projectID).collection("tasks").document(taskID).set(task)

        return {"success" : True, "task" : task}

    except Exception as e:
        return {"success" : False, "message" : str(e)}

@tasksRouter.get("/", status_code=status.HTTP_201_CREATED)
def getPersonalTasks(projectID: str,userID: str = Depends(statusProtected)):
    try:
        # Check if the project exists
        if Database.exists("projects", projectID) == False:
            return badRequestError("Project not found")

        tasks = db.collection("projects").document(projectID).collection("tasks").where("assignee", "==", userID).get()

        tasks = [task.to_dict() for task in tasks]
        return {"success" : True, "tasks" : tasks}

    except Exception as e:
        return {"success" : False, "message" : str(e)}
    
@tasksRouter.delete("/{taskID}", status_code=status.HTTP_201_CREATED)
def deleteTask(projectID: str,taskID: str,userID: str = Depends(statusProtected)):
    try:
        # Check if the user is the manager of the project
        project = Database.read("projects", projectID)
        if project is None:
            return badRequestError("Project not found")
        
        if project["manager"] != userID:
            return privilegeError("Only the manager can delete tasks")
        
        # Check if the task exists
        task = db.collection("projects").document(projectID).collection("tasks").document(taskID).get()
        if not task.exists:
            return badRequestError("Task does not exist")

        # Delete the task
        db.collection("projects").document(projectID).collection("tasks").document(taskID).delete()

        return {"success" : True,
                "message" : "Task deleted successfully"}

    except Exception as e:
        return {"success" : False, "message" : str(e)}
    
@tasksRouter.put("/{taskID}", status_code=status.HTTP_201_CREATED)
async def managerUpdateTask(projectID: str,taskID: str,request : dict,userID: str = Depends(statusProtected)):
    try:
        # Check if the user is the manager of the project
        project = Database.read("projects", projectID)
        if project is None:
            return badRequestError("Project not found")
        
        if project["manager"] != userID:
            return privilegeError("Only the manager can update tasks")


        task = request


        if task is None:
            return badRequestError("Task does not exist")

        db.collection("projects").document(projectID).collection("tasks").document(taskID).update(task)

        return {"success" : True,
                "message" : "Task updated successfully",
                }

    except Exception as e:
        return {"success" : False, "message" : str(e)}
    
@tasksRouter.put("/{taskID}/status", status_code=status.HTTP_201_CREATED)
async def userUpdateTask(projectID: str,taskID: str,request : dict,userID: str = Depends(statusProtected)):
    try:
        
        

        status = request["status"]

        print(status)
        # Check if the status is valid
        if status not in TaskState.__dict__.values():
            return badRequestError("Invalid status , should be [NEW,PRODUCT_BACKLOG,SPRINT_BACKLOG,IN_PROGRESS,IN_REVIEW,DONE]")
        # Check if the user is the manager of the project
        project = Database.read("projects", projectID)
        if project is None:
            return badRequestError("Project not found")
        
        task = db.collection("projects").document(projectID).collection("tasks").document(taskID).get()
        if not task.exists:
            return badRequestError("Task does not exist")
        task = task.to_dict()
        if task["assignee"] != userID:
            return privilegeError("Only the assignee can update the task status")
        

        task = {"status" : status}

        db.collection("projects").document(projectID).collection("tasks").document(taskID).update(task)

        return {"success" : True,
                "message" : "Task updated successfully",
                }

    except Exception as e:
        return {"success" : False, "message" : str(e)}
    
@tasksRouter.get("/{userMail}", status_code=status.HTTP_201_CREATED)
async def managerGetUserTasks(projectID:str,userMail: str,userID: str = Depends(statusProtected)):
    try:
        # Check if the user is the manager of the project
        project = Database.read("projects", projectID)
        if project is None:
            return badRequestError("Project does not exist")
        if project["manager"] != userID:
            return privilegeError("Only the manager can view tasks")
        
        user = db.collection("users").where("email", "==", userMail.lower()).get()
        if len(user) == 0:
            return badRequestError("User not found")
        user = user[0].to_dict()
        userID = user["id"]


        # Get the tasks
        tasks = db.collection("projects").document(projectID).collection("tasks").where("assignee", "==", userID).get()

        tasks = [task.to_dict() for task in tasks]
        return {"success" : True, "tasks" : tasks}

    except Exception as e:
        return {"success" : False, "message" : str(e)}
    

@tasksRouter.post("/", status_code=status.HTTP_201_CREATED)
async def addPersonalTask(projectID: str,request : AddPersonalTaskRequest,userID: str = Depends(statusProtected)):
    try:
        task = request.dict()
        if not isDateCorrect(task["deadline"]):
            return badRequestError("Invalid date format")
        taskID = str(uuid.uuid4())
        task["id"] = taskID
        task["status"] = TaskState.NEW
        task["assignee"] = userID
        # Create / Add a new task to the tasks collection
        db.collection("projects").document(projectID).collection("tasks").document(taskID).set(task)

        return {"success" : True, "task" : task}

    except Exception as e:
        return {"success" : False, "message" : str(e)}