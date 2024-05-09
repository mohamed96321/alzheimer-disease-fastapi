from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import numpy as np
import shutil
import uuid
from config.db import SessionLocal
from models.images import Image
from models.scans import Scan
from config.predictions import ImagePredictor

router = APIRouter()

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

    predictions = []

    # List to hold paths of uploaded images
    uploaded_image_paths = []

    try:
        # Process each uploaded image
        for image in images:
            # Save image to upload folder
            filename = os.path.join("uploads", f"{scan_id}-{image.filename}")
            with open(filename, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            # Append image path to the list of uploaded images
            uploaded_image_paths.append(filename)

            # Check if the saved image file is valid
            if not image_predictor.is_valid_image(filename):
                raise HTTPException(status_code=400, detail="Invalid image file")

            # Perform prediction
            try:
                prediction = image_predictor.predict_image(filename)
                predictions.append(prediction)
            except Exception as e:
                # If there's an error during prediction, raise it and handle cleanup later
                raise RuntimeError(f"Error predicting image: {e}")

            # Create Image entry in the database
            db_image = Image(scan_id=scan_id, image_path=filename, prediction=str(prediction))
            db.add(db_image)
        db.commit()

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

    except Exception as e:
        # If there's an error during processing, remove all uploaded images and raise HTTPException
        for uploaded_image_path in uploaded_image_paths:
            if os.path.exists(uploaded_image_path):
                os.remove(uploaded_image_path)
        raise HTTPException(status_code=400, detail=str(e))
