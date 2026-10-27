# -*- coding: utf-8 -*-
import unittest
from sanalpos_simulator.gateways import PayTRSimulator, IyzicoSimulator, SipaySimulator

class TestSanalPOSSimulator(unittest.TestCase):
    def test_paytr_hash_verification(self):
        payload, h = PayTRSimulator.create_payload(
            merchant_oid="SIPARIS-999",
            merchant_salt="salt_xyz",
            merchant_key="key_abc",
            amount_tl=250.0,
            status="success"
        )
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["total_amount"], "25000")
        self.assertTrue(PayTRSimulator.verify_hash(payload, "salt_xyz", "key_abc"))
        self.assertFalse(PayTRSimulator.verify_hash(payload, "wrong_salt", "key_abc"))

    def test_iyzico_payload_creation(self):
        payload = IyzicoSimulator.create_payload(
            conversation_id="CONV-1234",
            price=199.90,
            status="SUCCESS"
        )
        self.assertEqual(payload["status"], "SUCCESS")
        self.assertEqual(payload["price"], "199.90")
        self.assertTrue(len(payload["signature"]) > 10)

    def test_sipay_payload_creation(self):
        payload = SipaySimulator.create_payload(
            order_id="SPY-555",
            amount=450.0,
            status_code=100
        )
        self.assertEqual(payload["status_code"], 100)
        self.assertEqual(payload["total_amount"], "450.00")
        self.assertTrue("hash_key" in payload)

if __name__ == "__main__":
    unittest.main()
