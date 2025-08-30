from typing import Optional
from pydantic import BaseModel, Field


class ItemSearch(BaseModel):
    q: Optional[str] = Field(None, description="Search term for name or description")
    room_id: Optional[int] = Field(None, description="Filter by room")
    furniture_id: Optional[int] = Field(None, description="Filter by furniture")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Skip results (pagination)")
