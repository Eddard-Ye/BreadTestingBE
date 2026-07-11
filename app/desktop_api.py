"""pywebview 桌面端 JS API（供前端 window.pywebview.api 调用）。"""

from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import urlparse

import httpx
import webview

from app.core.config import Settings
from app.services.measurement_export import sanitize_export_filename

logger = logging.getLogger(__name__)

_EXPORT_PATH_PREFIX = "/api/v1/measurements/export"


class DesktopApi:
    def __init__(self, settings: Settings) -> None:
        self._base_url = f"http://{settings.DESKTOP_HOST}:{settings.DESKTOP_PORT}"

    def save_export(self, export_path: str, default_filename: str) -> dict:
        """打开系统「另存为」对话框，从本地后端下载 Excel 并写入用户选择的路径。"""
        if not export_path.startswith(_EXPORT_PATH_PREFIX):
            return {"ok": False, "message": "不允许的导出地址"}

        windows = webview.windows
        if not windows:
            return {"ok": False, "message": "桌面窗口未就绪"}

        window = windows[0]
        safe_name = sanitize_export_filename(default_filename)
        dialog_result = window.create_file_dialog(
            webview.FileDialog.SAVE,
            save_filename=safe_name,
            file_types=("Excel 文件 (*.xlsx)", "所有文件 (*.*)"),
        )
        if not dialog_result:
            return {"ok": False, "cancelled": True}

        save_path = Path(dialog_result[0] if isinstance(dialog_result, (list, tuple)) else dialog_result)
        if save_path.suffix.lower() != ".xlsx":
            save_path = save_path.with_suffix(".xlsx")

        url = f"{self._base_url}{export_path}"
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or parsed.hostname not in {"127.0.0.1", "localhost"}:
            return {"ok": False, "message": "不允许的导出地址"}

        try:
            response = httpx.get(url, timeout=120.0)
            response.raise_for_status()
            save_path.write_bytes(response.content)
            logger.info("Excel 已导出: %s", save_path)
            return {"ok": True, "path": str(save_path)}
        except httpx.HTTPError as exc:
            logger.warning("导出下载失败: %s", exc, exc_info=True)
            return {"ok": False, "message": "导出下载失败，请稍后重试"}
        except OSError as exc:
            logger.warning("导出写入失败: %s", exc, exc_info=True)
            return {"ok": False, "message": f"无法写入文件: {exc}"}
