#!/usr/bin/env python3
"""Serve the game for a headless browser smoke test.

Firefox's --screenshot fires at the `load` event, which for this game is long
before CreateJS has finished preloading and drawn anything.  This server
works around that:

  /check.html  the real lodeRunner.html with three changes --
               an error recorder injected ahead of every game script,
               `init()` called as soon as the DOM is parsed rather than at
               `load`, and a deliberately slow image that holds the `load`
               event open until the game has had time to draw.
  /__slow.png  a 1x1 PNG served after --delay seconds.

Run it, point `firefox --headless --screenshot` at /check.html, and the
screenshot shows the running game plus any JavaScript error that fired.
"""
from __future__ import annotations

import argparse
import base64
import functools
import http.server
import pathlib
import re
import time

ONE_PX_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB"
    "0C8AAAAASUVORK5CYII="
)

# Installed before any game script so a syntax or reference error in one of
# them still lands somewhere visible.
ERROR_RECORDER = """
<script>
window.__errs = [];
window.onerror = function(msg, src, line) {
  window.__errs.push(msg + "  (" + String(src).split('/').pop() + ":" + line + ")");
  return false;
};
window.addEventListener("unhandledrejection", function(e) {
  window.__errs.push("unhandled rejection: " + e.reason);
});
</script>
"""

# Starts the game at DOM-parse time and paints the error list over the page
# just before the screenshot is taken.
DRIVER = """
<script>
try { init(); } catch (e) { window.__errs.push("init() threw: " + e.message); }

setTimeout(function () {
  var d = document.createElement("div");
  d.style.cssText = "position:absolute;left:0;top:0;z-index:9999;font:bold 16px monospace;"
                  + "padding:6px;white-space:pre;max-width:100%%";
  if (window.__errs.length) {
    d.style.background = "#B00020";
    d.style.color = "#fff";
    d.textContent = "JS ERRORS (" + window.__errs.length + "):\\n" + window.__errs.join("\\n");
  } else {
    d.style.background = "#0A7D32";
    d.style.color = "#fff";
    d.textContent = "no JS errors; theme=" + (typeof curTheme === "undefined" ? "?" : curTheme);
  }
  document.body.appendChild(d);
}, %(paint_ms)d);
</script>
<img src="/__slow.png" style="position:absolute;left:-10px;top:-10px">
"""


class Handler(http.server.SimpleHTTPRequestHandler):
    delay = 12.0
    theme = None
    color = None

    def do_GET(self):  # noqa: N802  (http.server's casing)
        if self.path.startswith("/__slow.png"):
            time.sleep(self.delay)
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(ONE_PX_PNG)))
            self.end_headers()
            self.wfile.write(ONE_PX_PNG)
            return

        if self.path.startswith("/check.html"):
            self._serve_check()
            return

        super().do_GET()

    def _serve_check(self):
        html = pathlib.Path(self.directory, "lodeRunner.html").read_text()

        html = html.replace("<head>", "<head>\n" + ERROR_RECORDER, 1)
        html = html.replace(' onload="init()"', "")

        driver = DRIVER % {"paint_ms": int(self.delay * 1000) - 1500}
        if self.theme:
            # Force the theme (and optionally its colour) before init() runs.
            pre = '<script>try{setStorage(STORAGE_THEME_MODE, "%s");' % self.theme
            if self.color is not None:
                pre += ('setStorage(STORAGE_THEME_COLOR + "%s", %d);'
                        % (self.theme, self.color))
            pre += "}catch(e){}</script>\n"
            driver = pre + driver
        html = html.replace("</body>", driver + "\n</body>", 1)

        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8099)
    ap.add_argument("--delay", type=float, default=12.0,
                    help="seconds to hold the load event open")
    ap.add_argument("--theme", help="theme name to select before init()")
    ap.add_argument("--color", type=int, help="theme colour id (0 = original)")
    ap.add_argument("--root", type=pathlib.Path,
                    default=pathlib.Path(__file__).resolve().parent.parent)
    args = ap.parse_args()

    Handler.delay = args.delay
    Handler.theme = args.theme
    Handler.color = args.color
    handler = functools.partial(Handler, directory=str(args.root))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"serving {args.root} on http://127.0.0.1:{args.port}/check.html")
    srv.serve_forever()


if __name__ == "__main__":
    main()
