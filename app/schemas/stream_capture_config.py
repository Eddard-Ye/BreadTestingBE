from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class StreamCaptureConfigResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    host: str = Field(min_length=1, max_length=255)
    port: int = Field(ge=1, le=65535)
    timeout_seconds: float = Field(default=120.0, gt=0)
    height_scale: float = Field(default=1.0)
    height_offset: float = Field(default=0.0)


class StreamCaptureConfigUpdate(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    host: str = Field(min_length=1, max_length=255)
    port: int = Field(ge=1, le=65535)
    timeout_seconds: float | None = Field(default=None, gt=0)
    height_scale: float | None = None
    height_offset: float | None = None
