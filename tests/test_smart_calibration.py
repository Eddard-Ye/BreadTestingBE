from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.schemas.sensor import SensorReadingResponse, SerialPortConfig
from app.services.smart_calibration import SmartCalibrationService


def _weight_config(
    *,
    delta: float = 0.5,
    hold_seconds: float = 30.0,
    enable_mock: bool = False,
) -> SerialPortConfig:
    return SerialPortConfig(
        port="COM6",
        baud_rate="19200",
        data_bits="8",
        stop_bits="1",
        parity="None",
        enable_mock=enable_mock,
        smart_calibration_delta=delta,
        smart_calibration_hold_seconds=hold_seconds,
    )


def test_migrate_legacy_smart_calibration_enabled() -> None:
    from app.services.sensor_config_service import _migrate_serial_entry

    migrated = _migrate_serial_entry({"smartCalibrationEnabled": True}, "19200")
    assert migrated["smartCalibrationDelta"] == 0.5
    assert migrated["smartCalibrationHoldSeconds"] == 30.0

    disabled = _migrate_serial_entry({"smartCalibrationEnabled": False}, "19200")
    assert disabled["smartCalibrationDelta"] == 0.0


@patch("app.services.smart_calibration.time.time")
@patch("app.services.sensor_service.tare_weight")
@patch("app.services.sensor_service.read_weight")
@patch("app.services.smart_calibration.SmartCalibrationService._config")
def test_triggers_tare_when_below_delta_long_enough(
    mock_config: MagicMock,
    mock_read_weight: MagicMock,
    mock_tare_weight: MagicMock,
    mock_time: MagicMock,
) -> None:
    mock_config.return_value = _weight_config(delta=0.5, hold_seconds=30.0)
    mock_read_weight.return_value = SensorReadingResponse(value=0.2, connected=True)
    mock_tare_weight.return_value = SensorReadingResponse(value=0.0, connected=True)

    mock_time.side_effect = [100.0, 131.0]

    service = SmartCalibrationService()
    service._tick()
    mock_tare_weight.assert_not_called()

    service._tick()
    mock_tare_weight.assert_called_once()


@patch("app.services.smart_calibration.time.time")
@patch("app.services.sensor_service.tare_weight")
@patch("app.services.sensor_service.read_weight")
@patch("app.services.smart_calibration.SmartCalibrationService._config")
def test_resets_timer_when_reading_exceeds_delta(
    mock_config: MagicMock,
    mock_read_weight: MagicMock,
    mock_tare_weight: MagicMock,
    mock_time: MagicMock,
) -> None:
    mock_config.return_value = _weight_config(delta=0.5, hold_seconds=30.0)
    mock_time.side_effect = [100.0, 100.0, 110.0, 110.0, 135.0]
    mock_read_weight.side_effect = [
        SensorReadingResponse(value=0.2, connected=True),
        SensorReadingResponse(value=2.0, connected=True),
        SensorReadingResponse(value=0.1, connected=True),
        SensorReadingResponse(value=0.1, connected=True),
    ]

    service = SmartCalibrationService()
    service._tick()
    service._tick()
    service._tick()
    service._tick()
    mock_tare_weight.assert_not_called()


@patch("app.services.smart_calibration.SmartCalibrationService._config")
def test_disabled_when_delta_is_zero(mock_config: MagicMock) -> None:
    mock_config.return_value = _weight_config(delta=0.0, hold_seconds=30.0)

    service = SmartCalibrationService()
    service._tick()

    status = service.get_status()
    assert status["state"] == "disabled"
    assert status["enabled"] is False
