"""固定窗口大小的桌面应用启动器（内嵌系统 WebView 访问指定 URL）。"""

from __future__ import annotations

import logging
import sys
import threading
import time
from pathlib import Path

import uvicorn
import webview

from app.core.config import get_settings

logger = logging.getLogger(__name__)

SCROLL_LOCK_JS = (Path(__file__).with_name("desktop_scroll_lock.js")).read_text(encoding="utf-8")


def _run_server(host: str, port: int) -> None:
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        log_level="info",
    )


def _wait_for_server(url: str, timeout: float = 15.0) -> None:
    import httpx

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            response = httpx.get(url, timeout=1.0)
            if response.status_code < 500:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.2)

    raise RuntimeError(f"服务未在 {timeout}s 内就绪: {url}")


def _install_touch_scroll_lock(window: webview.Window) -> None:
    try:
        window.evaluate_js(SCROLL_LOCK_JS)
    except Exception:
        logger.warning("桌面滚动锁定脚本注入失败，已跳过", exc_info=True)


def _resolve_gui(gui: str | None) -> str | None:
    if gui:
        return gui
    if sys.platform == "win32":
        # Windows 默认必须用 Edge Chromium；MSHTML 无法运行现代前端且不支持 ES6 脚本
        return "edgechromium"
    return None


def launch_desktop() -> None:
    settings = get_settings()

    server_thread = threading.Thread(
        target=_run_server,
        args=(settings.DESKTOP_HOST, settings.DESKTOP_PORT),
        daemon=True,
        name="uvicorn-desktop",
    )
    server_thread.start()

    _wait_for_server(settings.DESKTOP_INIT_URL)

    window = webview.create_window(
        title=settings.DESKTOP_TITLE,
        url=settings.DESKTOP_INIT_URL,
        width=settings.DESKTOP_WIDTH,
        height=settings.DESKTOP_HEIGHT,
        resizable=settings.DESKTOP_RESIZABLE,
        min_size=(settings.DESKTOP_MIN_WIDTH, settings.DESKTOP_MIN_HEIGHT),
        zoomable=settings.DESKTOP_ZOOMABLE,
        frameless=settings.DESKTOP_FRAMELESS,
        easy_drag=settings.DESKTOP_EASY_DRAG,
        background_color=settings.DESKTOP_BACKGROUND_COLOR,
    )

    if settings.DESKTOP_DISABLE_TOUCH_SCROLL:
        window.events.loaded += _install_touch_scroll_lock

    gui = _resolve_gui(settings.DESKTOP_GUI)
    if gui:
        webview.start(gui=gui)
    else:
        webview.start()


if __name__ == "__main__":
    launch_desktop()
