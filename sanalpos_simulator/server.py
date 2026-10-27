# -*- coding: utf-8 -*-
"""
Webhook Dinleyici (Receiver) ve Gönderici (Sender) Motoru
"""

import urllib.request
import urllib.parse
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Optional

class WebhookReceiverHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length).decode("utf-8")

        print("\n" + "=" * 60)
        print(f"📥 [GELEN WEBHOOK POST İSTEĞİ] Yol: {self.path}")
        print("Headers:")
        for k, v in self.headers.items():
            print(f"  {k}: {v}")

        print("\nGövde (Body):")
        # Try JSON
        try:
            parsed_json = json.loads(post_body)
            print(json.dumps(parsed_json, indent=2, ensure_ascii=False))
        except Exception:
            # Form-urlencoded or raw text
            print(post_body)
        print("=" * 60)

        # Standard PayTR/İyzico response: 200 OK + "OK"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        # Suppress default server log to keep output clean
        return


def start_mock_receiver(port: int = 8080):
    server = HTTPServer(("0.0.0.0", port), WebhookReceiverHandler)
    print(f"🚀 Sanal POS Webhook Mock Dinleyicisi Başlatıldı: http://localhost:{port}")
    print("Testleriniz için gelen bildirimleri yakalamaya hazır... (Durdurmak için Ctrl+C)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSunucu kapatıldı.")
        server.server_close()


def send_webhook(url: str, payload: Dict[str, Any], as_json: bool = False) -> Dict[str, Any]:
    """
    Hedef backend sunucusuna webhook POST isteği fırlatır.
    """
    if as_json:
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json; charset=utf-8"}
    else:
        data = urllib.parse.urlencode(payload).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.status
            body = response.read().decode("utf-8", errors="replace")
            return {"success": True, "status_code": status, "response": body}
    except urllib.error.HTTPError as e:
        return {"success": False, "status_code": e.code, "response": e.read().decode("utf-8", errors="replace")}
    except Exception as e:
        return {"success": False, "status_code": 0, "error": str(e)}
