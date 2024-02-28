import socketio
from Core.Shared.SocketIO import sio
from Core.Shared.ErrorResponses import privilegeError
from Core.Shared.Security import decodeJwtToken
from Controllers.virtualEnvController import connectToVirtualEnvController, leaveVirtualEnvController, onDisconnectController, updatePositionController


socketIO = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    try:
        print(f"Connected: {sid}")

        # Extract the JWT token from the query string or headers

        headers = environ.get('asgi.scope', {}).get('headers', {})
        # Using a loop
        token = None
        for tpl in headers:
            if tpl[0].decode('utf-8') == 'authentication':
                token = tpl[1].decode('utf-8').split("Bearer ")[1] if "Bearer " in tpl[1].decode('utf-8') else tpl[1].decode('utf-8')
                break
        if not token:
            raise Exception("No valid JWT token provided")  

        # decodeJwtToken(token)
        

    except Exception as e:
        # Handle any exceptions raised during JWT decoding or validation
        await sio.disconnect(sid)
        print(f"Connection rejected: {e}")
        return Exception("Connection rejected: " + str(e))

@sio.event
async def disconnect(sid):
    print(f"Disconnected: {sid}")
    await onDisconnectController(sid)

@sio.event
async def connectToVirtualEnv(sid, environ):
    await connectToVirtualEnvController(sid, environ)

@sio.event
async def leaveVirtualEnv(sid, environ):
    await leaveVirtualEnvController(sid, environ)

@sio.event
async def updatePosition(sid, data):
    await updatePositionController(sid, data)



