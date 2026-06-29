from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import require_auth
from app.schemas.sensor import (
    SensorConfigResponse,
    SensorConfigUpdate,
    SensorReadingResponse,
    SerialPortsResponse,
)
from app.services.sensor_config_service import get_sensor_config_service, list_serial_ports
from app.services.sensor_service import (
    read_temperature,
    read_weight,
    tare_weight,
    zero_weight,
)

router = APIRouter()


@router.get("/config", response_model=SensorConfigResponse)
async def get_sensor_config() -> SensorConfigResponse:
    """获取温度、重量传感器的串口配置（含是否启用 Mock）。"""
    return get_sensor_config_service().get_config()


@router.put("/config", response_model=SensorConfigResponse)
async def update_sensor_config(
    payload: SensorConfigUpdate,
    _: Annotated[str, Depends(require_auth)],
) -> SensorConfigResponse:
    """保存串口配置到本地配置文件（需登录）。"""
    return get_sensor_config_service().save_config(payload)


@router.get("/ports", response_model=SerialPortsResponse)
async def get_serial_ports() -> SerialPortsResponse:
    """列出当前可用串口，供配置窗口下拉选择。"""
    return SerialPortsResponse(ports=list_serial_ports())


@router.get("/temperature", response_model=SensorReadingResponse)
async def get_current_temperature() -> SensorReadingResponse:
    """获取当前温度及温度传感器串口连接状态。"""
    reading = read_temperature()
    return SensorReadingResponse(value=reading.value, connected=reading.connected)


@router.get("/weight", response_model=SensorReadingResponse)
async def get_current_weight() -> SensorReadingResponse:
    """获取当前重量及重量传感器串口连接状态。"""
    reading = read_weight()
    return SensorReadingResponse(value=reading.value, connected=reading.connected)


@router.post("/weight/tare", response_model=SensorReadingResponse)
async def tare_current_weight() -> SensorReadingResponse:
    """对重量传感器执行去皮（校准）。"""
    reading = tare_weight()
    return SensorReadingResponse(value=reading.value, connected=reading.connected)


@router.post("/weight/zero", response_model=SensorReadingResponse)
async def zero_current_weight() -> SensorReadingResponse:
    """对重量传感器执行强制回零。"""
    reading = zero_weight()
    return SensorReadingResponse(value=reading.value, connected=reading.connected)
