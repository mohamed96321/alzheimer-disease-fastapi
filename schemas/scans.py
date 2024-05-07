from pydantic import BaseModel

class ScanBase(BaseModel):
    scan_id: str

class ScanCreate(ScanBase):
    pass

class Scan(ScanBase):
    id: int
    has_alzheimer: bool

    class Config:
        orm_mode = True
