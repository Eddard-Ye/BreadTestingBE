from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class SensorReadingResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    value: float
    connected: bool


class SerialPortConfig(BaseModel):
    """与前端串口配置窗口字段一致。"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    port: str = Field(min_length=1, max_length=64)
    baud_rate: str = Field(min_length=1, max_length=16)
    data_bits: str = Field(default="8", min_length=1, max_length=2)
    stop_bits: str = Field(default="1", min_length=1, max_length=3)
    parity: str = Field(default="None", min_length=1, max_length=16)
    enable_mock: bool = True


class SensorConfigResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    temperature: SerialPortConfig
    weight: SerialPortConfig
    height: SerialPortConfig


class SensorConfigUpdate(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    temperature: SerialPortConfig
    weight: SerialPortConfig
    height: SerialPortConfig


class SerialPortsResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    ports: list[str]
