from fastapi import FastAPI, HTTPException
from router.upload import router as upload_router
from router.scan import router as scan_router
from config.cors import add_cors_middleware
from utils.exceptions import handle_not_found, global_exception_handler

# Create FastAPI app
app = FastAPI()

# Include routers
app.include_router(upload_router)
app.include_router(scan_router)

# Add CORS middleware
add_cors_middleware(app)

# Add exception handlers as middleware
app.middleware("http")(handle_not_found)
app.middleware("http")(global_exception_handler)

# Run the FastAPI server by using uvicorn
# When you run uvicorn main:app (uvicorn main:app --reload), it runs on http://127.0.0.1:8000

# Run the FastAPI server by using python main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000)
