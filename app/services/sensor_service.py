import importlib.util
import random
import threading
from dataclasses import dataclass
from typing import Any, Callable

from app.schemas.sensor import SerialPortConfig
from app.services.sensor_config_service import get_sensor_config_service

_HW_DEFAULTS = {
    "temperature": {"slave_id": 1, "timeout": 1.0, "retries": 2},
    "weight": {"slave_id": 1, "timeout": 2.0, "retries": 2},
}

_KG_TO_G = 1000.0

_locks = {
    "temperature": threading.Lock(),
    "weight": threading.Lock(),
}
_sessions: dict[str, "_HwSession"] = {}
_mock_weight_lock = threading.Lock()
_mock_weight_value: float | None = None
_port_locks: dict[str, threading.Lock] = {}
_port_locks_guard = threading.Lock()


@dataclass(frozen=True)
class SensorReading:
    value: float
    connected: bool


@dataclass
class _HwSession:
    config_key: tuple[str, str, int, float, int]
    instance: Any
    connected: bool = False


def _serial_available() -> bool:
    return importlib.util.find_spec("serial") is not None


def _mock_reading(precision: int = 2) -> SensorReading:
    return SensorReading(
        value=round(random.uniform(0, 100), precision),
        connected=True,
    )


def _mock_weight_reading() -> SensorReading:
    with _mock_weight_lock:
        if _mock_weight_value is None:
            value = round(random.uniform(0, 100), 1)
        else:
            value = round(_mock_weight_value + random.uniform(-0.2, 0.2), 1)
    return SensorReading(value=value, connected=True)


def _set_mock_weight_baseline(value: float = 0.0) -> SensorReading:
    global _mock_weight_value
    with _mock_weight_lock:
        _mock_weight_value = value
    return SensorReading(value=round(value, 1), connected=True)


def _reset_mock_weight_state() -> None:
    global _mock_weight_value
    with _mock_weight_lock:
        _mock_weight_value = None


def _port_lock(port: str) -> threading.Lock:
    with _port_locks_guard:
        lock = _port_locks.get(port)
        if lock is None:
            lock = threading.Lock()
            _port_locks[port] = lock
        return lock


def _hw_params(config: SerialPortConfig, sensor_key: str) -> dict:
    defaults = _HW_DEFAULTS[sensor_key]
    return {
        "port": config.port,
        "baudrate": int(config.baud_rate),
        "slave_id": defaults["slave_id"],
        "timeout": defaults["timeout"],
        "retries": defaults["retries"],
    }


def _config_key(config: SerialPortConfig, sensor_key: str) -> tuple[str, str, int, float, int]:
    params = _hw_params(config, sensor_key)
    return (
        params["port"],
        str(params["baudrate"]),
        params["slave_id"],
        params["timeout"],
        params["retries"],
    )


def _serial_is_open(instance: Any) -> bool:
    ser = getattr(instance, "_ser", None)
    return ser is not None and ser.is_open


def _close_session(sensor_key: str) -> None:
    session = _sessions.pop(sensor_key, None)
    if session is None:
        return
    try:
        session.instance.close()
    except Exception:
        pass


def invalidate_sensor_sessions(sensor_key: str | None = None) -> None:
    """Close cached hardware sessions after config changes or mock mode."""
    if sensor_key is None:
        keys = list(_sessions.keys())
        _reset_mock_weight_state()
    else:
        keys = [sensor_key]
        if sensor_key == "weight":
            _reset_mock_weight_state()
    for key in keys:
        with _locks[key]:
            _close_session(key)


def _with_hw_session(
    sensor_key: str,
    config: SerialPortConfig,
    factory: Callable[[], Any],
    operation: Callable[[Any], float],
    precision: int,
) -> SensorReading:
    if not _serial_available():
        return SensorReading(value=0.0, connected=False)

    key = _config_key(config, sensor_key)
    sensor_lock = _locks[sensor_key]

    with _port_lock(config.port):
        with sensor_lock:
            session = _sessions.get(sensor_key)
            if (
                session is not None
                and session.connected
                and session.config_key == key
                and _serial_is_open(session.instance)
            ):
                instance = session.instance
            else:
                if session is not None:
                    _close_session(sensor_key)
                instance = factory()
                try:
                    instance.open()
                except Exception:
                    try:
                        instance.close()
                    except Exception:
                        pass
                    return SensorReading(value=0.0, connected=False)
                _sessions[sensor_key] = _HwSession(
                    config_key=key,
                    instance=instance,
                    connected=True,
                )

        try:
            value = operation(instance)
        except Exception:
            with sensor_lock:
                _close_session(sensor_key)
            return SensorReading(value=0.0, connected=False)

        with sensor_lock:
            active = _sessions.get(sensor_key)
            if active is not None:
                active.connected = True
        return SensorReading(value=round(value, precision), connected=True)


def _read_with_session(
    sensor_key: str,
    config: SerialPortConfig,
    factory: Callable[[], Any],
    read_fn: Callable[[Any], float],
    precision: int,
) -> SensorReading:
    return _with_hw_session(sensor_key, config, factory, read_fn, precision)


def _read_temperature_hw(config: SerialPortConfig) -> SensorReading:
    from app.services.rs485_temperature import Rs485Thermometer

    params = _hw_params(config, "temperature")

    def factory() -> Rs485Thermometer:
        return Rs485Thermometer(
            port=params["port"],
            baudrate=params["baudrate"],
            slave_id=params["slave_id"],
            timeout=params["timeout"],
            retries=params["retries"],
        )

    return _read_with_session(
        "temperature",
        config,
        factory,
        lambda sensor: sensor.read(),
        precision=2,
    )


def _with_weight_session(
    config: SerialPortConfig,
    operation: Callable[[Any], float],
    precision: int = 1,
) -> SensorReading:
    from app.services.km11_weight import Km11WeightTransmitter

    params = _hw_params(config, "weight")

    def factory() -> Km11WeightTransmitter:
        return Km11WeightTransmitter(
            port=params["port"],
            baudrate=params["baudrate"],
            slave_id=params["slave_id"],
            timeout=params["timeout"],
            retries=params["retries"],
        )

    return _with_hw_session("weight", config, factory, operation, precision)


def _read_weight_hw(config: SerialPortConfig) -> SensorReading:
    return _with_weight_session(
        config,
        lambda sensor: round(sensor.read_net().value * _KG_TO_G, 1),
        precision=1,
    )


def _tare_weight_hw(config: SerialPortConfig) -> SensorReading:
    def tare_and_read(sensor: Any) -> float:
        sensor.tare()
        return round(sensor.read_net().value * _KG_TO_G, 1)

    return _with_weight_session(config, tare_and_read, precision=1)


def _zero_weight_hw(config: SerialPortConfig) -> SensorReading:
    def zero_and_read(sensor: Any) -> float:
        sensor.zero()
        return round(sensor.read_net().value * _KG_TO_G, 1)

    return _with_weight_session(config, zero_and_read, precision=1)


def read_temperature() -> SensorReading:
    """读取当前温度及串口连接状态（含校准偏移）。"""
    config = get_sensor_config_service().get_config().temperature
    if config.enable_mock:
        reading = _mock_reading(precision=2)
    else:
        reading = _read_temperature_hw(config)

    if not reading.connected:
        return reading

    calibrated = round(reading.value + config.calibration_delta, 2)
    return SensorReading(value=calibrated, connected=True)


def read_weight() -> SensorReading:
    """读取当前重量及串口连接状态。"""
    config = get_sensor_config_service().get_config().weight
    if config.enable_mock:
        return _mock_weight_reading()
    return _read_weight_hw(config)


def tare_weight() -> SensorReading:
    """对重量传感器执行去皮，并返回去皮后的读数（克）。"""
    config = get_sensor_config_service().get_config().weight
    if config.enable_mock:
        return _set_mock_weight_baseline(0.0)
    return _tare_weight_hw(config)


def zero_weight() -> SensorReading:
    """对重量传感器执行强制回零，并返回回零后的读数（克）。"""
    config = get_sensor_config_service().get_config().weight
    if config.enable_mock:
        return _set_mock_weight_baseline(0.0)
    return _zero_weight_hw(config)
