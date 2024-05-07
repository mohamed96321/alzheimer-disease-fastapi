from pydantic import BaseModel

class ImageBase(BaseModel):
    scan_id: str
    image_path: str
    prediction: str

class ImageCreate(ImageBase):
    pass

class Image(ImageBase):
    id: int

    class Config:
        orm_mode = True
