# -*- coding: utf-8 -*-
"""
Sanal POS Webhook Simülatörü CLI
"""

import sys
import argparse
import json
from .gateways import PayTRSimulator, IyzicoSimulator, SipaySimulator
from .server import start_mock_receiver, send_webhook

def main():
    parser = argparse.ArgumentParser(
        description="Türkiye Sanal POS (PayTR, İyzico, Sipay) Webhook Callback & Hash Simülatörü"
    )
    subparsers = parser.add_subparsers(dest="command", help="Komutlar: send, listen, hash")

    # Send command
    send_parser = subparsers.add_parser("send", help="Hedef e-ticaret sitenize sahte ödeme callback bildirimi gönderir")
    send_parser.add_argument("--gateway", choices=["paytr", "iyzico", "sipay"], default="paytr", help="Ödeme kuruluşu")
    send_parser.add_argument("--url", required=True, help="Hedef webhook bildirim URL'si (örn: http://localhost:8000/callback)")
    send_parser.add_argument("--order-id", default="", help="Sipariş / Sepet Referans No")
    send_parser.add_argument("--amount", type=float, default=100.0, help="Tutar (TL)")
    send_parser.add_argument("--status", choices=["success", "failed"], default="success", help="Ödeme durumu")
    send_parser.add_argument("--salt", default="test_salt_123", help="Merchant Salt (PayTR)")
    send_parser.add_argument("--key", default="test_key_456", help="Merchant Key (PayTR)")

    # Listen command
    listen_parser = subparsers.add_parser("listen", help="Gelen bildirimleri yakalamak için lokalde mock dinleyici sunucusu açar")
    listen_parser.add_argument("--port", type=int, default=8080, help="Dinlenecek yerel port")

    # Hash command
    hash_parser = subparsers.add_parser("hash", help="Sanal POS hash ve imza doğrulaması yapar")
    hash_parser.add_argument("--gateway", choices=["paytr", "sipay"], default="paytr")
    hash_parser.add_argument("--order-id", required=True)
    hash_parser.add_argument("--amount", required=True)
    hash_parser.add_argument("--salt", default="test_salt_123")
    hash_parser.add_argument("--key", default="test_key_456")

    args = parser.parse_args()

    if args.command == "listen":
        start_mock_receiver(args.port)
        return

    if args.command == "hash":
        if args.gateway == "paytr":
            h = PayTRSimulator.generate_hash(args.order_id, args.salt, "success", args.amount, args.key)
            print(f"PayTR HMAC-SHA256 Token: {h}")
        return

    if args.command == "send":
        if args.gateway == "paytr":
            payload, _ = PayTRSimulator.create_payload(
                merchant_oid=args.order_id,
                merchant_salt=args.salt,
                merchant_key=args.key,
                amount_tl=args.amount,
                status=args.status
            )
            print(f"📡 PayTR Webhook Bildirimi Gönderiliyor -> {args.url}")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            res = send_webhook(args.url, payload, as_json=False)
        elif args.gateway == "iyzico":
            payload = IyzicoSimulator.create_payload(
                conversation_id=args.order_id,
                price=args.amount,
                status="SUCCESS" if args.status == "success" else "FAILURE"
            )
            print(f"📡 İyzico Webhook Bildirimi Gönderiliyor -> {args.url}")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            res = send_webhook(args.url, payload, as_json=True)
        elif args.gateway == "sipay":
            payload = SipaySimulator.create_payload(
                order_id=args.order_id,
                amount=args.amount,
                status_code=100 if args.status == "success" else -1
            )
            print(f"📡 Sipay Webhook Bildirimi Gönderiliyor -> {args.url}")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            res = send_webhook(args.url, payload, as_json=True)

        print("\n📥 Yanıt:")
        print(f"HTTP Kodu: {res.get('status_code')}")
        print(f"İçerik: {res.get('response', res.get('error'))}")
        if res.get("response", "").strip() == "OK":
            print("✅ Backend 'OK' yanıtı döndü; işlem başarıyla onaylandı!")
        return

    parser.print_help()

if __name__ == "__main__":
    main()
