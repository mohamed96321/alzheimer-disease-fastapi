from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from structlog import get_logger

# Set up logging
logger = get_logger()

# Define a route not found exception handler
async def handle_not_found(request: Request, call_next):
    response = await call_next(request)
    if response.status_code == 404:
        return JSONResponse({"message": "unfound api request"}, status_code=404)
    return response

# Define a global exception handler
async def global_exception_handler(request, call_next):
    try:
        return await call_next(request)
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    except SQLAlchemyError as exc:
        logger.error(f"SQLAlchemy error: {exc}")
        raise HTTPException(status_code=500, detail="Oops, something get wrong in the database")
    except Exception as exc:
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
