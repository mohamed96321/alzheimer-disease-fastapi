from pydantic import BaseModel

# Define Pydantic models for input validation
class ScanBase(BaseModel):
    scan_id: str
    alzheimer_percent: str
    has_alzheimer: bool
