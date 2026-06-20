from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class SensorReadingResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    value: float = Field(ge=0, le=100)
    connected: bool
