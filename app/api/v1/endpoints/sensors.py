from fastapi import APIRouter

from app.schemas.sensor import SensorReadingResponse
from app.services.sensor_service import read_height, read_temperature, read_weight

router = APIRouter()


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


@router.get("/height", response_model=SensorReadingResponse)
async def get_current_height() -> SensorReadingResponse:
    """获取当前高度及高度传感器串口连接状态。"""
    reading = read_height()
    return SensorReadingResponse(value=reading.value, connected=reading.connected)
