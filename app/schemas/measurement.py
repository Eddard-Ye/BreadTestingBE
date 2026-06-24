from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

RecordType = Literal["product", "bottom", "middle"]


class MeasurementBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    recipe_id: str = Field(min_length=1)
    record_type: RecordType
    slot_index: int = Field(ge=0)
    sample_name: str = Field(min_length=1)
    temperature: str
    weight: str
    length: str
    width: str
    height: str
    water_cut_width: str
    preview_name: str | None = None
    recorded_at: datetime | None = None


class MeasurementCreate(MeasurementBase):
    pass


class MeasurementBatchCreate(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    records: list[MeasurementCreate] = Field(min_length=1)


class MeasurementResponse(MeasurementBase):
    id: str
    recorded_at: datetime


class MeasurementListResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    records: list[MeasurementResponse]
    total: int
    page: int
    page_size: int
