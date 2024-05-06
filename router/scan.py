from fastapi import FastAPI, UploadFile, File, HTTPException # type: ignore
from config.db import SessionLocal
from models.images import Image
from models.scans import Scan

# Create FastAPI app
app = FastAPI()

# Retrieve scan information endpoint
@app.get("/scan/{scan_id}")
async def get_scan(scan_id: str):
    db = SessionLocal()
    db_scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()

    if not db_scan:
        raise HTTPException(status_code=404, detail="Scan ID not found")

    images = db.query(Image).filter(Image.scan_id == scan_id).all()

    image_paths = [img.image_path for img in images]
    return {
        "scan_id": db_scan.scan_id,
        "has_alzheimer": db_scan.has_alzheimer,
        "images": image_paths,
        "predictions": [img.prediction for img in images]
    }
