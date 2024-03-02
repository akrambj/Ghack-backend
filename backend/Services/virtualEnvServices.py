from Core.Shared.SocketIO import sio
from Core.Shared.Database import Database

async def connectToVirtualEnv(virtualEnvId: str, userId  :str, userSid: str):
    
    await sio.enter_room(userSid, virtualEnvId)
    await sio.emit("newUser", {
        "virtualEnvId": virtualEnvId,
        "newConnectedUser": userSid, 
        "userId": userId
        # "connectedUserId": userSid
        }, room=virtualEnvId, skip_sid=userSid)
    
    connectedUsers = Database.read("virtualEnv", virtualEnvId)
    if  connectedUsers:
        connectedUsers = connectedUsers.get("connectedUsers", [])
    else:
        connectedUsers = []
    
    connectedUsers.append({
        "userId": userId,
        "userSid": userSid
    })
    
    Database.store("virtualEnv", virtualEnvId, {
        "connectedUsers": connectedUsers,
    })


    connectedUsers = [item for item in connectedUsers if item.get("userId") != userId]
    

    await sio.emit("connectedSuccessfuly", {
        "connectedClients": connectedUsers
    }, room=userSid)


async def leaveVirtualEnv(virtualEnvId: str, userSid: str):
    await sio.leave_room(userSid, virtualEnvId)
    print("leaving virtual env: ", virtualEnvId)
    connectedUsers = Database.read("virtualEnv", virtualEnvId)
    if connectedUsers:
        connectedUsers = connectedUsers.get("connectedUsers", [])
        
        
        userId = ""
        for user in connectedUsers:
            print("user: ", user)
            if user.get("userSid") == userSid:
                userId = user.get("userId")
        await sio.emit("userLeft", {
            "leftUser": userId

        }, room=virtualEnvId, skip_sid=userSid)
        connectedUsers = [item for item in connectedUsers if item.get("userId") != userId]
    else:
        connectedUsers = []
    Database.store("virtualEnv", virtualEnvId, {
        "connectedUsers": connectedUsers
    })
    
    print("connected users: ", connectedUsers)

async def updatePosition(virtualEnvId: str, userSid: str, data: dict):
    data["updatedUser"] = userSid
    await sio.emit("updatePosition", data, room=virtualEnvId, skip_sid=userSid)

async def onDisconnect(sid):
    rooms =  sio.rooms(sid)
    for room in rooms:
        if room != sid:    
            await leaveVirtualEnv(room, sid)