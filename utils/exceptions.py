from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

# Define a route not found exception handler
async def handle_not_found(request: Request, call_next):
    response = await call_next(request)
    if response.status_code == 404:
        return JSONResponse({"message": "unfound api request"}, status_code=404)
    return response

# Define a global exception handler
async def global_exception_handler(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as http_exception:
        return JSONResponse({"detail": http_exception.detail}, status_code=http_exception.status_code)
    except Exception as e:
        # Catch all unexpected errors
        return JSONResponse({"message": "Internal Server Error"}, status_code=500)
