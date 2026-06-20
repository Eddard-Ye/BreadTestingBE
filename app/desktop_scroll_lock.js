(function () {
  if (window.__breadDesktopScrollLock) {
    return;
  }
  window.__breadDesktopScrollLock = true;

  const style = document.createElement("style");
  style.textContent = `
    html, body, #root {
      overflow: hidden !important;
      overscroll-behavior: none !important;
      touch-action: none !important;
    }
  `;
  (document.head || document.documentElement).appendChild(style);

  const blockScroll = (event) => {
    event.preventDefault();
  };

  const listenerOptions = { passive: false, capture: true };

  window.addEventListener("wheel", blockScroll, listenerOptions);
  window.addEventListener("touchmove", blockScroll, listenerOptions);
  window.addEventListener("scroll", blockScroll, listenerOptions);

  window.addEventListener(
    "touchstart",
    (event) => {
      if (event.touches.length > 1) {
        event.preventDefault();
      }
    },
    listenerOptions,
  );

  ["gesturestart", "gesturechange", "gestureend"].forEach((eventName) => {
    window.addEventListener(eventName, blockScroll, listenerOptions);
  });

  window.addEventListener(
    "keydown",
    (event) => {
      const scrollKeys = new Set([
        "ArrowUp",
        "ArrowDown",
        "ArrowLeft",
        "ArrowRight",
        "PageUp",
        "PageDown",
        "Home",
        "End",
        " ",
      ]);
      if (scrollKeys.has(event.key)) {
        event.preventDefault();
      }
    },
    listenerOptions,
  );
})();
