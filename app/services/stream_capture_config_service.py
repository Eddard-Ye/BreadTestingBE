from __future__ import annotations

import json
from pathlib import Path

from app.core.config import Settings, get_settings
from app.schemas.stream_capture_config import (
    StreamCaptureConfigResponse,
    StreamCaptureConfigUpdate,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def resolve_stream_capture_config_path(config_path: str | None = None) -> Path:
    raw_path = (
        config_path
        if config_path is not None
        else get_settings().STREAM_CAPTURE_CONFIG_PATH
    )
    path = Path(raw_path)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


def default_stream_capture_config(settings: Settings | None = None) -> StreamCaptureConfigResponse:
    current = settings or get_settings()
    return StreamCaptureConfigResponse(
        host=current.STREAM_CAPTURE_HOST,
        port=current.STREAM_CAPTURE_PORT,
        timeout_seconds=current.STREAM_CAPTURE_TIMEOUT_SECONDS,
    )


class StreamCaptureConfigService:
    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or resolve_stream_capture_config_path()

    def get_config(self) -> StreamCaptureConfigResponse:
        if not self.config_path.exists():
            config = default_stream_capture_config()
            self.save_config(
                StreamCaptureConfigUpdate(
                    host=config.host,
                    port=config.port,
                    timeout_seconds=config.timeout_seconds,
                    height_scale=config.height_scale,
                    height_offset=config.height_offset,
                )
            )
            return config

        raw = json.loads(self.config_path.read_text(encoding="utf-8"))
        return StreamCaptureConfigResponse.model_validate(raw)

    def save_config(self, payload: StreamCaptureConfigUpdate) -> StreamCaptureConfigResponse:
        current = self.get_config() if self.config_path.exists() else default_stream_capture_config()
        config = StreamCaptureConfigResponse(
            host=payload.host.strip(),
            port=payload.port,
            timeout_seconds=(
                payload.timeout_seconds
                if payload.timeout_seconds is not None
                else current.timeout_seconds
            ),
            height_scale=(
                payload.height_scale
                if payload.height_scale is not None
                else current.height_scale
            ),
            height_offset=(
                payload.height_offset
                if payload.height_offset is not None
                else current.height_offset
            ),
        )
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.config_path.with_suffix(".json.tmp")
        temp_path.write_text(
            json.dumps(config.model_dump(by_alias=True), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp_path.replace(self.config_path)
        return config


def get_stream_capture_config_service() -> StreamCaptureConfigService:
    return StreamCaptureConfigService()
