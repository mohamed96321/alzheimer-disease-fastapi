from fastapi import FastAPI, HTTPException # type: ignore
from config.cors import add_cors_middleware
from router.upload import upload_images
from router.scan import get_scan
from utils.exceptions import not_found_exception_handler, global_exception_handler

# Create FastAPI app
app = FastAPI()

# Add CORS add_cors_middleware
add_cors_middleware(app)

# Include routers
app.include_router(upload_images, prefix="/upload")
app.include_router(get_scan, prefix="/scan")

# Add not found exception handlers
app.add_exception_handler(HTTPException, not_found_exception_handler)

# Add global exception handlers
app.add_exception_handler(Exception, global_exception_handler)

# Run the FastAPI server by using uvicorn
# When you run uvicorn main:app (uvicorn main:app --reload), it runs on http://127.0.0.1:8000

# Or Run the FastAPI server by using python main.py or filename.py
if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run(app, host="127.0.0.1", port=3000)
