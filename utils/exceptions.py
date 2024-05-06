from fastapi import FastAPI, HTTPException # type: ignore
from fastapi.responses import JSONResponse # type: ignore

app = FastAPI()

# Define a route not found exception handler
@app.exception_handler(HTTPException)
async def not_found_exception_handler(request, exc):
    if exc.status_code == 404:
        return JSONResponse(status_code=404, content={"message": "unfound api request"})
    raise exc

# Define a global exception handler
@app.middleware("http")
async def global_exception_handler(request, call_next):
    try:
        return await call_next(request)
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
