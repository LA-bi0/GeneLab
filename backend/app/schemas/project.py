from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    owner_id: str = Field(min_length=1, max_length=36)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    organism: str | None = Field(default=None, max_length=255)
    visibility: str = Field(default="private", min_length=1, max_length=50)


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    name: str
    description: str | None
    organism: str | None
    visibility: str
    created_at: datetime
    updated_at: datetime