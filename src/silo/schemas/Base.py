from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TimestampSchema(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BaseSchema(BaseModel):
    
    model_config = ConfigDict(from_attributes=True)