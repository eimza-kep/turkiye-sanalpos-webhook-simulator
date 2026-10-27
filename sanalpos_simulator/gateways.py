# -*- coding: utf-8 -*-
"""
Sanal POS Sağlayıcıları İçin Webhook Payload ve Hash Hesaplayıcıları
"""

import hmac
import hashlib
import base64
import time
import uuid
from typing import Dict, Any, Tuple

class PayTRSimulator:
    """PayTR iFrame ve Direkt API Bildirim (Webhook) Simülatörü"""

    @staticmethod
    def generate_hash(merchant_oid: str, merchant_salt: str, status: str, total_amount: str, merchant_key: str) -> str:
        """
        PayTR HMAC-SHA256 Token Algoritması:
        token = base64(hmac_sha256(merchant_oid + merchant_salt + status + total_amount, merchant_key))
        """
        hash_str = f"{merchant_oid}{merchant_salt}{status}{total_amount}"
        digest = hmac.new(
            merchant_key.encode("utf-8"),
            hash_str.encode("utf-8"),
            hashlib.sha256
        ).digest()
        return base64.b64encode(digest).decode("utf-8")

    @classmethod
    def create_payload(
        cls,
        merchant_oid: str = "",
        merchant_salt: str = "test_salt_123",
        merchant_key: str = "test_key_456",
        amount_tl: float = 100.0,
        status: str = "success",
        failed_reason: str = ""
    ) -> Tuple[Dict[str, str], str]:
        if not merchant_oid:
            merchant_oid = f"SIPARIS-{int(time.time())}"

        # PayTR tutarı kuruş cinsinden (örn: 100 TL = 10000 kuruş) gönderir
        total_amount_kurus = str(int(amount_tl * 100))

        generated_hash = cls.generate_hash(
            merchant_oid=merchant_oid,
            merchant_salt=merchant_salt,
            status=status,
            total_amount=total_amount_kurus,
            merchant_key=merchant_key
        )

        payload = {
            "merchant_oid": merchant_oid,
            "status": status,
            "total_amount": total_amount_kurus,
            "hash": generated_hash,
            "failed_reason_code": "0" if status == "success" else "99",
            "failed_reason_msg": "" if status == "success" else (failed_reason or "Yetersiz Bakiye"),
            "payment_type": "card",
            "currency": "TL",
            "payment_amount": total_amount_kurus
        }
        return payload, generated_hash

    @classmethod
    def verify_hash(cls, post_data: Dict[str, str], merchant_salt: str, merchant_key: str) -> bool:
        expected_hash = cls.generate_hash(
            merchant_oid=post_data.get("merchant_oid", ""),
            merchant_salt=merchant_salt,
            status=post_data.get("status", ""),
            total_amount=post_data.get("total_amount", ""),
            merchant_key=merchant_key
        )
        return hmac.compare_digest(expected_hash, post_data.get("hash", ""))


class IyzicoSimulator:
    """İyzico Checkout Form ve Ödeme Bildirimi Simülatörü"""

    @staticmethod
    def generate_signature(secret_key: str, token: str, payment_id: str) -> str:
        data = f"{token}:{payment_id}"
        digest = hmac.new(
            secret_key.encode("utf-8"),
            data.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return digest

    @classmethod
    def create_payload(
        cls,
        conversation_id: str = "",
        payment_id: str = "",
        secret_key: str = "sandbox_secret_key_789",
        price: float = 150.0,
        status: str = "SUCCESS"
    ) -> Dict[str, Any]:
        if not conversation_id:
            conversation_id = f"CONV-{int(time.time())}"
        if not payment_id:
            payment_id = str(uuid.uuid4().int)[:10]

        token = f"iyzi-token-{uuid.uuid4().hex[:16]}"
        signature = cls.generate_signature(secret_key, token, payment_id)

        return {
            "status": status,
            "paymentId": payment_id,
            "conversationId": conversation_id,
            "token": token,
            "price": f"{price:.2f}",
            "paidPrice": f"{price:.2f}",
            "currency": "TRY",
            "signature": signature,
            "mdStatus": "1" if status == "SUCCESS" else "0"
        }


class SipaySimulator:
    """Sipay Güvenli Ödeme Bildirimi Simülatörü"""

    @staticmethod
    def generate_hash(order_id: str, amount: str, app_secret: str) -> str:
        hash_str = f"{order_id}|{amount}|{app_secret}"
        return hashlib.sha256(hash_str.encode("utf-8")).hexdigest()

    @classmethod
    def create_payload(
        cls,
        order_id: str = "",
        amount: float = 250.0,
        app_secret: str = "sipay_test_secret",
        status_code: int = 100
    ) -> Dict[str, Any]:
        if not order_id:
            order_id = f"SPY-{int(time.time())}"
        amount_str = f"{amount:.2f}"
        s_hash = cls.generate_hash(order_id, amount_str, app_secret)

        return {
            "order_id": order_id,
            "invoice_id": f"INV-{order_id}",
            "status_code": status_code,
            "status_description": "İşlem Başarılı" if status_code == 100 else "İşlem Reddedildi",
            "total_amount": amount_str,
            "currency_code": "TRY",
            "hash_key": s_hash
        }
