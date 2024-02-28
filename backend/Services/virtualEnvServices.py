from Core.Shared.SocketIO import sio
from Core.Shared.Database import Database

async def connectToVirtualEnv(virtualEnvId: str, userSid: str):
    
    await sio.enter_room(userSid, virtualEnvId)
    await sio.emit("newUser", {
        "virtualEnvId": virtualEnvId,
        "newConnectedUser": userSid, 
        # "connectedUserId": userSid
        }, room=virtualEnvId, skip_sid=userSid)
    
    connectedUsers = Database.read("virtualEnv", virtualEnvId)
    if  connectedUsers:
        connectedUsers = connectedUsers.get("connectedUsers", [])
    else:
        connectedUsers = []
    
    connectedUsers.append(userSid)
    
    Database.store("virtualEnv", virtualEnvId, {
        "connectedUsers": connectedUsers
    })

    connectedUsers.remove(userSid)
    

    await sio.emit("connectedSuccessfuly", {
        "connectedClients": connectedUsers
    }, room=userSid)


async def leaveVirtualEnv(virtualEnvId: str, userSid: str):
    await sio.leave_room(userSid, virtualEnvId)
    await sio.emit("userLeft", {
        "leftUser": userSid
    }, room=virtualEnvId, skip_sid=userSid)
    connectedUsers = Database.read("virtualEnv", virtualEnvId)
    if connectedUsers:
        connectedUsers = connectedUsers.get("connectedUsers", [])

        if userSid in connectedUsers:
            connectedUsers.remove(userSid)
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