from starlette.responses import JSONResponse

def privilegeError(message):
    """
    Raises an HTTPException with a 403 status code (Forbidden).

    Args:
        message (str): The error message to be included in the response.

    Returns:
        JSONResponse: A JSON response with the error message and status code.
    """
    return JSONResponse(
        content={"success":False,"message":"AUTHORIZATION ERROR: " + message},
        status_code=403
    )

def badRequestError(message):
    """
    Raises an HTTPException with a 400 status code (Bad Request).

    Args:
        message (str): The error message to be included in the response.

    Returns:
        JSONResponse: A JSON response with the error message and status code.
    """
    return JSONResponse(
        content={"success":False,"message":"BAD REQUEST: " + message},
        status_code=400
    )