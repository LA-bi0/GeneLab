from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    name: str
    file_name: str
    file_format: str
    file_size: int
    checksum: str
    sequence_length: int | None
    gc_content: float | None
    status: str
    error_message: str | None
    created_at: datetime