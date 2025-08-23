from datetime import datetime
from pydantic import Field

from silo.models import Base

class Session(Base):
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.now(datetime.timezone.utc))
