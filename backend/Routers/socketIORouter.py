import socketio

sio = socketio.AsyncServer(async_mode="asgi")
socketIO = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    try:
        # Extract the JWT token from the query string or headers
        
        headers = environ.get('asgi.scope', {}).get('headers', {})
        # Using a loop
        token = None
        for tpl in headers:
            print(str(tpl[0]))
            if str(tpl[0]) == 'authentication':
                print("Found token")
                token = tpl[1].split("Bearer ")[1] if "Bearer " in tpl[1] else tpl[1]
                break

        print(token)

        # Validate and decode the JWT token
        # if token:
        #     decoded_info = decodeJWTToken(token)

        #     # Optionally, you can use the decoded information for further authorization checks
        #     # For example, check user roles, permissions, etc.

        #     print(f"Client connected: {sid}")
        #     print(f"Decoded JWT Info: {decoded_info}")

        # else:
        #     # Reject the connection if no valid JWT token is provided
        #     await sio.disconnect(sid)
        #     print(f"Connection rejected: No valid JWT token")

    except Exception as e:
        # Handle any exceptions raised during JWT decoding or validation
        await sio.disconnect(sid)
        print(f"Connection rejected: {str(e)}")



