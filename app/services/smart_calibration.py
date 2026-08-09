"""Smart calibration monitor — auto-tares when weight stays below delta.

State machine:
    DISABLED  → smart_calibration_delta == 0
    IDLE      → enabled but reading not below delta (or mock / disconnected)
    MONITORING→ reading below delta, accumulating hold time
    TRIGGERED → auto-tare fired, transitioning to COOLDOWN
    COOLDOWN  → post-trigger grace period, then back to IDLE
"""

from __future__ import annotations

import logging
import threading
import time

logger = logging.getLogger(__name__)

_POLL_INTERVAL_S = 2.0
_COOLDOWN_S = 120.0


class SmartCalibrationService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._below_since: float | None = None
        self._state: str = "disabled"
        self._cooldown_until: float = 0.0
        self._last_message: str | None = None
        self._last_value: float | None = None
        self._stopped = False
        self._thread: threading.Thread | None = None

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

    def get_status(self) -> dict:
        with self._lock:
            hold_elapsed = None
            if self._below_since is not None:
                hold_elapsed = round(time.time() - self._below_since, 1)

            return {
                "enabled": self._state != "disabled",
                "state": self._state,
                "last_value_g": self._last_value,
                "hold_elapsed_s": hold_elapsed,
                "last_message": self._last_message,
            }

    def _config(self):
        from app.services.sensor_config_service import get_sensor_config_service

        return get_sensor_config_service().get_config().weight

    def _run(self) -> None:
        while not self._stopped:
            stopped_event = threading.Event()
            stopped_event.wait(timeout=_POLL_INTERVAL_S)
            if self._stopped:
                return

            try:
                self._tick()
            except Exception:
                logger.exception("Smart calibration tick failed, will retry")

    def _reset_monitoring(self) -> None:
        self._below_since = None
        if self._state not in {"cooldown", "triggered"}:
            self._state = "idle"

    def _tick(self) -> None:
        try:
            config = self._config()
            delta = float(config.smart_calibration_delta)
            hold_seconds = float(config.smart_calibration_hold_seconds)
            enabled = delta != 0
        except Exception:
            logger.warning("Cannot read sensor config, skipping tick")
            return

        now = time.time()

        with self._lock:
            if now < self._cooldown_until:
                self._state = "cooldown"
                return

            if not enabled or hold_seconds <= 0:
                self._state = "disabled"
                self._below_since = None
                return

            if config.enable_mock:
                self._state = "idle"
                self._below_since = None
                return

        try:
            from app.services.sensor_service import read_weight

            reading = read_weight()
        except Exception:
            logger.warning("Weight read failed during smart calibration tick")
            return

        with self._lock:
            if not reading.connected:
                self._reset_monitoring()
                return

            value = reading.value
            self._last_value = value
            threshold = abs(delta)

            if abs(value) >= threshold:
                self._reset_monitoring()
                return

            if self._below_since is None:
                self._below_since = now
                self._state = "monitoring"
                return

            elapsed = now - self._below_since
            if elapsed < hold_seconds:
                self._state = "monitoring"
                return

            try:
                from app.services.sensor_service import tare_weight

                tare_weight()
                self._state = "triggered"
                self._cooldown_until = now + _COOLDOWN_S
                self._last_message = (
                    f"智能校准已触发 (读数 {value:.2f}g < {threshold:g}g, "
                    f"持续 {elapsed:.0f}s)"
                )
                logger.info(self._last_message)
            except Exception:
                self._state = "idle"
                self._last_message = "智能校准触发失败，请手动校准"
                logger.warning(self._last_message)
            self._below_since = None


_instance: SmartCalibrationService | None = None
_instance_lock = threading.Lock()


def get_smart_calibration_service() -> SmartCalibrationService:
    global _instance
    with _instance_lock:
        if _instance is None:
            _instance = SmartCalibrationService()
        return _instance
