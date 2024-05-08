from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import numpy as np
import os
import shutil
import uuid
from config.db import SessionLocal
from models.images import Image
from models.scans import Scan
from config.predictions import ImagePredictor

router = APIRouter()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

model_folder_name = "my_model"
model_path = os.path.abspath(model_folder_name)
image_predictor = ImagePredictor(model_path)

@router.post("/upload")
async def upload_images(images: List[UploadFile] = File(...)):
    if not images:
        raise HTTPException(status_code=400, detail="No images uploaded")

    scan_id = str(uuid.uuid4())

    db = SessionLocal()
    db_scan = Scan(scan_id=scan_id)
    db.add(db_scan)
    db.commit()

    predictions = []

    for image in images:
        # Check file extension to ensure it's an image
        file_extension = image.filename.split('.')[-1]
        if file_extension.lower() not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Invalid file type: {image.filename}")

        # Save image to upload folder
        filename = os.path.join("uploads", f"{scan_id}-{image.filename}")
        with open(filename, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Perform prediction
        try:
            prediction = image_predictor.predict_image(filename)
            predictions.append(prediction)
        except Exception as e:
            prediction = "Prediction failed"
            print(f"Error predicting image: {e}")

        # Create Image entry in the database
        db_image = Image(scan_id=scan_id, image_path=filename, prediction=str(prediction))
        db.add(db_image)
        db.commit()

    if predictions:
        # Normalize predictions to range [0, 1]
        normalized_predictions = [pred / 3.2 for pred in predictions]  # Assuming the maximum prediction value is 3
        avg_prediction = np.mean(normalized_predictions)
        alzheimerPercent = round(avg_prediction * 100, 2)
        hasAlzheimer = alzheimerPercent >= 70
        formatted_percent = "{:.2f}%".format(alzheimerPercent)

        # Update Scan entry in the database with has_alzheimer value
        db_scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
        db_scan.has_alzheimer = hasAlzheimer
        db_scan.alzheimer_percent = formatted_percent
        db.commit()

    return {"scan_id": scan_id}
