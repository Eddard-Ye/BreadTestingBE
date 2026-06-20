import random
from dataclasses import dataclass


@dataclass(frozen=True)
class SensorReading:
    value: float
    connected: bool


def read_temperature() -> SensorReading:
    """读取当前温度及串口连接状态，后续可替换为真实设备驱动。"""
    return SensorReading(
        value=round(random.uniform(0, 100), 2),
        connected=True,
    )


def read_weight() -> SensorReading:
    """读取当前重量及串口连接状态，后续可替换为真实设备驱动。"""
    return SensorReading(
        value=round(random.uniform(0, 100), 2),
        connected=True,
    )
