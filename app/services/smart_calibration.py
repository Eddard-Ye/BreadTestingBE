"""Smart calibration monitor — auto-tares weight sensor when readings stabilise.

State machine:
    DISABLED  → toggle off, clear all readings
    IDLE      → enabled but no qualifying readings (zero, disconnected, mock, unstable)
    MONITORING→ accumulating stable non-zero readings
    TRIGGERED → auto-tare fired, transitioning to COOLDOWN
    COOLDOWN  → 120 s post-trigger grace period, then back to IDLE
"""

from __future__ import annotations

import logging
import threading
import time

logger = logging.getLogger(__name__)

_POLL_INTERVAL_S = 2.0
_WINDOW_S = 60.0            # total look-back window
_MIN_READINGS = 15           # must have at least this many data points
_MIN_DURATION_S = 30.0       # must span at least this much real time
_STABILITY_THRESHOLD_G = 0.5  # max deviation from mean
_COOLDOWN_S = 120.0          # post-trigger cooldown


class SmartCalibrationService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._readings: list[tuple[float, float]] = []  # (value_g, timestamp)
        self._state: str = "idle"
        self._cooldown_until: float = 0.0
        self._last_message: str | None = None
        self._stopped = False
        self._thread: threading.Thread | None = None

    # -- lifecycle -------------------------------------------------------

    def start(self) -> None:
        if self._thread is not None:
            return
        self._stopped = False
        self._thread = threading.Thread(target=self._run, daemon=True, name="smart-cal")
        self._thread.start()
        logger.info("Smart calibration monitor started")

    def stop(self) -> None:
        self._stopped = True
        if self._thread is not None:
            self._thread.join(timeout=5.0)
        self._thread = None
        logger.info("Smart calibration monitor stopped")

    # -- public status ---------------------------------------------------

    def get_status(self) -> dict:
        with self._lock:
            values = [v for v, _ in self._readings]
            if values and len(values) >= 2:
                mean = sum(values) / len(values)
                stability = round(max(abs(v - mean) for v in values), 2)
            else:
                stability = None

            return {
                "enabled": self._state != "disabled",
                "state": self._state,
                "readings_collected": len(self._readings),
                "required_readings": _MIN_READINGS,
                "stability_g": stability,
                "last_message": self._last_message,
            }

    # -- internal --------------------------------------------------------

    def _config(self):
        from app.services.sensor_config_service import get_sensor_config_service
        return get_sensor_config_service().get_config().weight

    def _run(self) -> None:
        while not self._stopped:
            self._stopped_event = threading.Event()
            self._stopped_event.wait(timeout=_POLL_INTERVAL_S)
            if self._stopped:
                return

            try:
                self._tick()
            except Exception:
                logger.exception("Smart calibration tick failed, will retry")

    def _tick(self) -> None:
        try:
            config = self._config()
            enabled = config.smart_calibration_enabled
        except Exception:
            logger.warning("Cannot read sensor config, skipping tick")
            return

        now = time.time()

        with self._lock:
            # -- Cooldown check (before anything else) -------------------
            if now < self._cooldown_until:
                self._state = "cooldown"
                return

            # -- Disabled → reset ----------------------------------------
            if not enabled:
                self._state = "disabled"
                self._readings.clear()
                return

            # -- Mock mode → skip ----------------------------------------
            if config.enable_mock:
                self._state = "idle"
                self._readings.clear()
                return

        # -- Read weight (outside lock to avoid deadlock with hw session) -
        try:
            from app.services.sensor_service import read_weight
            reading = read_weight()
        except Exception:
            logger.warning("Weight read failed during smart calibration tick")
            return

        with self._lock:
            # -- Disconnected → reset ------------------------------------
            if not reading.connected:
                self._state = "idle"
                self._readings.clear()
                return

            value = reading.value

            # -- Zero / near-zero → reset --------------------------------
            if abs(value) < 0.01:
                self._state = "idle"
                self._readings.clear()
                return

            # -- Append + trim window ------------------------------------
            self._readings.append((value, now))
            cutoff = now - _WINDOW_S
            self._readings = [(v, t) for v, t in self._readings if t > cutoff]

            if len(self._readings) < _MIN_READINGS:
                self._state = "monitoring"
                return

            values = [v for v, _ in self._readings]
            mean_val = sum(values) / len(values)
            max_dev = max(abs(v - mean_val) for v in values)
            duration = now - self._readings[0][1]

            if max_dev <= _STABILITY_THRESHOLD_G and duration >= _MIN_DURATION_S:
                # ---- Trigger auto-calibration ----
                try:
                    from app.services.sensor_service import tare_weight
                    tare_weight()
                    self._state = "triggered"
                    self._cooldown_until = now + _COOLDOWN_S
                    self._last_message = (
                        f"智能校准已触发 (均值 {mean_val:.1f}g, 波动±{max_dev:.2f}g)"
                    )
                    logger.info(self._last_message)
                except Exception:
                    self._state = "idle"
                    self._last_message = "智能校准触发失败，请手动校准"
                    logger.warning(self._last_message)
                self._readings.clear()
            else:
                self._state = "monitoring"


# -- singleton -----------------------------------------------------------

_instance: SmartCalibrationService | None = None
_instance_lock = threading.Lock()


def get_smart_calibration_service() -> SmartCalibrationService:
    global _instance
    with _instance_lock:
        if _instance is None:
            _instance = SmartCalibrationService()
        return _instance
