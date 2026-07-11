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
from app.desktop_api import DesktopApi

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


def _windows_primary_screen_geometry() -> tuple[int, int, int, int]:
    """主屏 (x, y, width, height)。frameless + maximized 在 Windows 上不可靠，创建时直接铺满。"""
    try:
        screen = webview.screens[0]
        return screen.x, screen.y, screen.width, screen.height
    except Exception:
        logger.warning("无法读取 webview.screens，回退 Win32 GetSystemMetrics", exc_info=True)
        user32 = __import__("ctypes").windll.user32
        return 0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def _build_window_kwargs(settings) -> dict:
    common = {
        "title": settings.DESKTOP_TITLE,
        "url": settings.DESKTOP_INIT_URL,
        "resizable": settings.DESKTOP_RESIZABLE,
        "min_size": (settings.DESKTOP_MIN_WIDTH, settings.DESKTOP_MIN_HEIGHT),
        "zoomable": settings.DESKTOP_ZOOMABLE,
        "frameless": settings.DESKTOP_FRAMELESS,
        "easy_drag": settings.DESKTOP_EASY_DRAG,
        "background_color": settings.DESKTOP_BACKGROUND_COLOR,
        "fullscreen": settings.DESKTOP_FULLSCREEN,
    }

    if sys.platform == "win32" and not settings.DESKTOP_FULLSCREEN:
        x, y, width, height = _windows_primary_screen_geometry()
        logger.info("Windows 桌面窗口: x=%s y=%s width=%s height=%s", x, y, width, height)
        return {
            **common,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "maximized": False,
        }

    return {
        **common,
        "width": settings.DESKTOP_WIDTH,
        "height": settings.DESKTOP_HEIGHT,
        "maximized": settings.DESKTOP_MAXIMIZED,
    }


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

    api = DesktopApi(settings)
    window = webview.create_window(**_build_window_kwargs(settings), js_api=api)

    if settings.DESKTOP_DISABLE_TOUCH_SCROLL:
        window.events.loaded += _install_touch_scroll_lock

    webview.settings["ALLOW_DOWNLOADS"] = True
    gui = _resolve_gui(settings.DESKTOP_GUI)
    if gui:
        webview.start(gui=gui)
    else:
        webview.start()


if __name__ == "__main__":
    launch_desktop()
