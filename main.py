from fastapi import FastAPI, UploadFile, File, HTTPException # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey # type: ignore
from sqlalchemy.orm import sessionmaker, relationship # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from typing import List # type: ignore
import uuid
import os
import shutil
import tensorflow as tf # type: ignore
import numpy as np # type: ignore
from PIL import Image as PILImage # type: ignore
from sqlalchemy.exc import ProgrammingError # type: ignore
from starlette.middleware.cors import CORSMiddleware # type: ignore

# Create FastAPI app
app = FastAPI()

# Configure SQLAlchemy database
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:1372002@localhost/alzheimers"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define database models
class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String(36), unique=True, index=True)
    has_alzheimer = Column(Boolean, default=False)
    images = relationship("Image", back_populates="scan")

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String(36), ForeignKey('scans.scan_id'))
    image_path = Column(String(255))
    prediction = Column(String(36), default="")
    scan = relationship("Scan", back_populates="images")

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
except ProgrammingError as e:
    raise RuntimeError(f"Error creating database tables: {e}")

# Define image predictor class
class ImagePredictor:
    def __init__(self, model_path):
        self.model = self.load_model(model_path)

    def load_model(self, model_path):
        try:
            model = tf.saved_model.load(model_path)
            print("Loaded model successfully")
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            raise RuntimeError("Failed to load model")
        
    def preprocess_image(self, image_path):
        # Load image using PIL
        img = PILImage.open(image_path)

        # Convert image to RGB if it's not already
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize image to (150, 150)
        img = img.resize((150, 150))

        # Convert image to numpy array
        img_array = np.array(img)

        # Normalize pixel values to range [0, 1]
        img_array = img_array.astype(np.float32) / 255.0

        # Ensure image has 3 channels (RGB)
        if img_array.shape[-1] != 3:
            raise ValueError("Image must have 3 channels (RGB)")

        # Expand dimensions to create batch dimension (None, 150, 150, 3)
        img_array = tf.expand_dims(img_array, axis=0)

        return img_array

    def predict_image(self, image_path):
        if self.model is None:
            raise ValueError("Model is not loaded or is invalid.")

        # Preprocess the image
        img_array = self.preprocess_image(image_path)

        try:
            # Perform inference
            predictions = self.model(img_array)
            predicted_class_index = np.argmax(predictions)
            return float(predicted_class_index)  # Convert prediction to float
        except Exception as e:
            print(f"Error predicting image: {e}")
            raise RuntimeError("Failed to predict image")

# Create an instance of the image predictor
model_folder_name = "my_model"
model_path = os.path.abspath(model_folder_name)
image_predictor = ImagePredictor(model_path)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Handle image upload endpoint
@app.post("/upload")
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

    # Calculate average prediction
    if predictions:
        avg_prediction = np.mean(predictions)
        has_alzheimer = avg_prediction > 0.5  # Adjust threshold as needed

        # Update Scan entry in the database with has_alzheimer value
        db_scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
        db_scan.has_alzheimer = has_alzheimer
        db.commit()

    return {"scan_id": scan_id}

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Request", "Authorization"],
)

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

# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000)
