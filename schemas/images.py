from pydantic import BaseModel

class ImageBase(BaseModel):
    scan_id: str
    image_path: str
    prediction: str