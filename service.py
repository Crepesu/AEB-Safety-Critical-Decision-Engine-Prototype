"""Minimal HTTP(S) service exposing health and sample decision endpoints.

Used by the Jenkins Deploy + Monitoring stages to demonstrate runtime checks.
Security Notes:
        * Defaults to plain HTTP for simplicity, triggering Sonar hotspot S5332.
            To satisfy scanners, optional TLS can be enabled by providing the
            environment variables SERVICE_CERT_FILE and SERVICE_KEY_FILE. When both
            are present the server wraps with SSLContext.
        * This service is not production‑grade; no auth / rate limiting.
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import ssl
from typing import Any

try:
    from aeb.core.system import AEBSystem  # type: ignore
except Exception:  # pragma: no cover - service still offers /health
    AEBSystem = None  # fallback if import fails in minimal runtime


class _Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: Any):  # helper
        data = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802 (BaseHTTPRequestHandler naming)
        if self.path == "/health":
            self._send(200, {"status": "ok"})
            return
        if self.path == "/sample-decision":
            if AEBSystem is None:
                self._send(500, {"error": "AEBSystem unavailable"})
                return
            system = AEBSystem()
            scenario = [{
                "type": "pedestrian",
                "position": [12.0, 0.0],
                "velocity": [0, 0],
                "size": [0.6, 1.8],
            }]
            result = system.process_scenario(scenario)
            self._send(200, {"decision": result["decision"], "min_ttc": result["min_ttc"]})
            return
        self._send(404, {"error": "not found"})


def run():  # pragma: no cover - integration behaviour tested via pipeline curl
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), _Handler)
    cert = os.environ.get("SERVICE_CERT_FILE")
    key = os.environ.get("SERVICE_KEY_FILE")
    if cert and key and os.path.exists(cert) and os.path.exists(key):
        # Create secure TLS context (no deprecated protocols)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain(certfile=cert, keyfile=key)
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
        scheme = "https"
    else:
        scheme = "http"
    print(f"[service] Listening on {scheme}://0.0.0.0:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[service] Shutting down")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()