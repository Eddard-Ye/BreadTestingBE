from __future__ import annotations

from typing import Any
from urllib.parse import quote

import httpx
from fastapi import HTTPException, status

from app.schemas.capture import CaptureMeasurementResponse
from app.schemas.recipe import DEFAULT_HEIGHT_CALC_MODE, HeightCalcMode
from app.services.sensor_service import read_temperature, read_weight
from app.services.stream_capture_config_service import get_stream_capture_config_service


def _stream_base_url() -> str:
    config = get_stream_capture_config_service().get_config()
    return f"http://{config.host}:{config.port}"


def build_capture_preview_path(file_name: str) -> str:
    return f"/api/v1/capture/preview/{quote(file_name, safe='')}"


def _validate_capture_file_name(file_name: str) -> str:
    cleaned = file_name.strip()
    if not cleaned or "/" in cleaned or "\\" in cleaned or ".." in cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的图片文件名",
        )
    return cleaned

def _format_sensor_text(value: float, *, unit: str = "", precision: int = 1) -> str:
    text = f"{value:.{precision}f}"
    return f"{text}{unit}" if unit else text


def _pick_field(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload and payload[key] is not None:
            return payload[key]
    return None


def _normalize_required_text(value: Any) -> str:
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="视觉采集服务返回数据不完整",
        )
    text = str(value).strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="视觉采集服务返回数据不完整",
        )
    return text


def _normalize_metric(value: Any, *, precision: int = 1) -> str:
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="视觉采集服务返回数据不完整",
        )
    if isinstance(value, (int, float)):
        return f"{float(value):.{precision}f}"
    text = str(value).strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="视觉采集服务返回数据不完整",
        )
    return text


def capture_measurement(
    *,
    name: str,
    water_cut: bool,
    height_calc_mode: HeightCalcMode = DEFAULT_HEIGHT_CALC_MODE,
) -> CaptureMeasurementResponse:
    """读取传感器并调用 capture_2d_stream 的 POST /capture 接口。"""
    temperature_reading = read_temperature()
    weight_reading = read_weight()

    temperature_text = _format_sensor_text(temperature_reading.value, precision=1)
    weight_text = _format_sensor_text(weight_reading.value, unit="g", precision=2)
    height_text = "0.0mm"

    stream_config = get_stream_capture_config_service().get_config()
    capture_url = f"{_stream_base_url()}/capture"
    payload = {
        "name": name.strip(),
        "height": height_text,
        "temperature": temperature_text,
        "weight": weight_text,
        "water_cut": bool(water_cut),
        "height_calc_mode": height_calc_mode,
        "height_scale": stream_config.height_scale,
        "height_offset": stream_config.height_offset,
    }

    try:
        with httpx.Client(timeout=stream_config.timeout_seconds) as client:
            response = client.post(capture_url, json=payload)
            response.raise_for_status()
            body = response.json() if response.content else {"ok": True}
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text.strip() or f"HTTP {exc.response.status_code}"
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"视觉采集服务请求失败: {detail}",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"无法连接视觉采集服务: {exc}",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="视觉采集服务返回非 JSON 响应",
        ) from exc

    if isinstance(body, dict) and body.get("ok") is False:
        message = _pick_field(body, "error", "message", "detail") or "视觉采集失败"
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(message),
        )

    if not isinstance(body, dict):
        body = {}

    length = _normalize_metric(
        _pick_field(body, "length_mm", "lengthMm", "length", "Length"),
        precision=1,
    )
    width = _normalize_metric(
        _pick_field(body, "width_mm", "widthMm", "width", "Width"),
        precision=1,
    )
    water_cut_mm_raw = _pick_field(body, "water_cut_mm", "waterCutMm", "water_cut_width")
    if water_cut:
        water_cut_mm = _normalize_metric(water_cut_mm_raw, precision=1)
    else:
        water_cut_mm = "0"

    height_raw = _pick_field(body, "height_mm", "heightMm", "height", "Height")
    if height_raw is None and isinstance(body.get("record"), dict):
        height_raw = _pick_field(body["record"], "height_mm", "heightMm", "height", "Height")
    height = _normalize_metric(height_raw, precision=1)

    file_name = _normalize_required_text(_pick_field(body, "fileName", "file_name"))

    return CaptureMeasurementResponse(
        ok=True,
        temperature=f"{temperature_reading.value:.1f}",
        weight=f"{weight_reading.value:.2f}",
        height=height,
        length=length,
        width=width,
        water_cut_mm=water_cut_mm,
        file_name=file_name,
        image_preview_url=build_capture_preview_path(file_name),
    )


def fetch_capture_preview(file_name: str) -> tuple[bytes, str]:
    """从视觉服务 GET /captures/{fileName} 拉取抓拍图片。"""
    safe_name = _validate_capture_file_name(file_name)
    preview_url = f"{_stream_base_url()}/captures/{quote(safe_name, safe='')}"

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(preview_url)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "image/jpeg")
            return response.content, content_type
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text.strip() or f"HTTP {exc.response.status_code}"
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"获取抓拍图片失败: {detail}",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"无法连接视觉采集服务: {exc}",
        ) from exc
