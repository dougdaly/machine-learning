from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class DataMode(str, Enum):
    synthetic = "synthetic"
    existing = "existing"


class ServiceName(str, Enum):
    entitlements = "entitlements"
    generic = "generic"


class RequestType(str, Enum):
    load_data = "load_data"


class DataGenerationRequest(BaseModel):
    request_type: Literal["load_data"] = "load_data"
    service: ServiceName = ServiceName.entitlements
    data_mode: DataMode = DataMode.synthetic
    start_date: str = Field(..., description="Inclusive start date in YYYY-MM-DD")
    end_date: str = Field(..., description="Inclusive end date in YYYY-MM-DD")
    output_prefix: Optional[str] = Field(
        default="synthetic/raw",
        description="S3 prefix or local output prefix",
    )

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_iso_date(cls, value: str) -> str:
        parts = value.split("-")
        if len(parts) != 3:
            raise ValueError(f"Date must be YYYY-MM-DD, got: {value}")
        yyyy, mm, dd = parts
        if len(yyyy) != 4 or len(mm) != 2 or len(dd) != 2:
            raise ValueError(f"Date must be YYYY-MM-DD, got: {value}")
        return value
