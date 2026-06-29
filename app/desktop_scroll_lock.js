(function () {
  if (window.__breadDesktopScrollLock) {
    return;
  }
  window.__breadDesktopScrollLock = true;

  var style = document.createElement("style");
  style.textContent =
    "html, body, #root {" +
    "overflow: hidden !important;" +
    "overscroll-behavior: none !important;" +
    "touch-action: none !important;" +
    "}";
  (document.head || document.documentElement).appendChild(style);

  function blockScroll(event) {
    event.preventDefault();
  }

  function blockMultiTouch(event) {
    if (event.touches && event.touches.length > 1) {
      event.preventDefault();
    }
  }

  function blockScrollKeys(event) {
    var key = event.key || event.keyCode;
    if (
      key === "ArrowUp" ||
      key === "ArrowDown" ||
      key === "ArrowLeft" ||
      key === "ArrowRight" ||
      key === "PageUp" ||
      key === "PageDown" ||
      key === "Home" ||
      key === "End" ||
      key === " " ||
      key === 32 ||
      key === 33 ||
      key === 34 ||
      key === 35 ||
      key === 36 ||
      key === 37 ||
      key === 38 ||
      key === 39 ||
      key === 40
    ) {
      event.preventDefault();
    }
  }

  var capture = true;
  window.addEventListener("wheel", blockScroll, capture);
  window.addEventListener("touchmove", blockScroll, capture);
  window.addEventListener("scroll", blockScroll, capture);
  window.addEventListener("touchstart", blockMultiTouch, capture);
  window.addEventListener("keydown", blockScrollKeys, capture);

  var gestureEvents = ["gesturestart", "gesturechange", "gestureend"];
  for (var i = 0; i < gestureEvents.length; i += 1) {
    window.addEventListener(gestureEvents[i], blockScroll, capture);
  }
})();
