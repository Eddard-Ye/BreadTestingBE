from __future__ import annotations

import json
from pathlib import Path

from app.core.config import get_settings
from app.schemas.sensor import SensorConfigResponse, SensorConfigUpdate, SerialPortConfig

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _default_serial_config(baud_rate: str) -> SerialPortConfig:
    return SerialPortConfig(
        port="COM6",
        baud_rate=baud_rate,
        data_bits="8",
        stop_bits="1",
        parity="None",
        enable_mock=True,
    )


def _default_temperature_config() -> SerialPortConfig:
    return _default_serial_config("9600")


def _default_weight_config() -> SerialPortConfig:
    return _default_serial_config("38400")


def _default_height_config() -> SerialPortConfig:
    return _default_serial_config("115200")


def default_sensor_config() -> SensorConfigResponse:
    return SensorConfigResponse(
        temperature=_default_temperature_config(),
        weight=_default_weight_config(),
        height=_default_height_config(),
    )


def resolve_sensor_config_path(config_path: str | None = None) -> Path:
    raw_path = config_path if config_path is not None else get_settings().SENSOR_CONFIG_PATH
    path = Path(raw_path)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


def _migrate_serial_entry(raw: dict, default_baud: str) -> dict:
    baud = raw.get("baudRate")
    if baud is None:
        baud = raw.get("baudrate", default_baud)
    return {
        "port": raw.get("port", "COM6"),
        "baudRate": str(baud),
        "dataBits": raw.get("dataBits", "8"),
        "stopBits": raw.get("stopBits", "1"),
        "parity": raw.get("parity", "None"),
        "enableMock": raw.get("enableMock", True),
    }


def _migrate_config_raw(raw: dict) -> dict:
    defaults = {
        "temperature": "9600",
        "weight": "38400",
        "height": "115200",
    }
    migrated: dict = {}
    for key, baud in defaults.items():
        entry = raw.get(key)
        if isinstance(entry, dict):
            migrated[key] = _migrate_serial_entry(entry, baud)
        else:
            migrated[key] = _migrate_serial_entry({}, baud)
    return migrated


class SensorConfigService:
    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or resolve_sensor_config_path()

    def get_config(self) -> SensorConfigResponse:
        if not self.config_path.exists():
            config = default_sensor_config()
            self.save_config(SensorConfigUpdate.model_validate(config.model_dump()))
            return config

        raw = json.loads(self.config_path.read_text(encoding="utf-8"))
        migrated = _migrate_config_raw(raw)
        config = SensorConfigResponse.model_validate(migrated)
        if migrated != raw:
            self.save_config(SensorConfigUpdate.model_validate(migrated))
        return config

    def save_config(self, payload: SensorConfigUpdate) -> SensorConfigResponse:
        config = SensorConfigResponse.model_validate(payload.model_dump())
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.config_path.with_suffix(".json.tmp")
        temp_path.write_text(
            json.dumps(config.model_dump(by_alias=True), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp_path.replace(self.config_path)
        from app.services.sensor_service import invalidate_sensor_sessions

        invalidate_sensor_sessions()
        return config


def get_sensor_config_service() -> SensorConfigService:
    return SensorConfigService()


def list_serial_ports() -> list[str]:
    try:
        from serial.tools import list_ports

        return [
            port.device
            for port in list_ports.comports()
            if port.device.upper().startswith("COM")
        ]
    except ImportError:
        return []
