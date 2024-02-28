
from Services.virtualEnvServices import connectToVirtualEnv, leaveVirtualEnv, onDisconnect, updatePosition

async def connectToVirtualEnvController(sid, data):
    try:
        # Decode the token
        virtualEnvId = data.get("virtualEnvId", "")
        if not virtualEnvId:
            raise Exception("No virtualEnvId provided")
         
        await connectToVirtualEnv(virtualEnvId, sid)
    except Exception as e:
        print(f"Connection rejected: {e}")

async def leaveVirtualEnvController(sid, data):
    try:
        # Decode the token
        virtualEnvId = data.get("virtualEnvId", "")
        if not virtualEnvId:
            raise Exception("No virtualEnvId provided")
        await leaveVirtualEnv(virtualEnvId, sid)
    except Exception as e:
        print(f"Connection rejected: {e}")

async def onDisconnectController(sid):
    try:
        await onDisconnect(sid)
    except Exception as e:
        print(f"Connection rejected: {e}")

async def updatePositionController(sid, data):
    try:
        # Decode the token
        virtualEnvId = data.get("virtualEnvId", "")
        if not virtualEnvId:
            raise Exception("No virtualEnvId provided")
        await updatePosition(virtualEnvId, sid, data)
    except Exception as e:
        print(f"Connection rejected: {e}")

