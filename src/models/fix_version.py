from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class FixVersion(BaseModel):
    """Model for JIRA fix versions (releases)."""
    id: str = Field(..., description="Unique identifier for the fix version")
    name: str = Field(..., description="Name of the fix version (e.g., '1.0.0')")
    description: str = Field(..., description="Description of what this fix version contains")
    release_date: datetime = Field(..., description="Planned release date for this version")
    released: bool = Field(False, description="Whether this version has been released")
    archived: bool = Field(False, description="Whether this version has been archived") 