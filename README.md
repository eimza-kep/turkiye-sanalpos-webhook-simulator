# Türkiye Sanal POS Webhook Callback & Hash Simülatörü 💳⚡

[![Lisans: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Desteklenenler: PayTR, İyzico, Sipay](https://img.shields.io/badge/Gateways-PayTR%20%7C%20%C4%B0yzico%20%7C%20Sipay-emerald.svg)](https://eticaretokulu.com.tr)
[![Bağımlılık: Sıfır](https://img.shields.io/badge/Dependencies-Zero--Dependency-success.svg)](https://github.com)
[![Rehber](https://img.shields.io/badge/Rehber-Sanal%20POS%20Rehberi-f59e0b.svg)](https://eticaretokulu.com.tr)

Türkiye'de faaliyet gösteren lisanslı ödeme kuruluşları (**PayTR, İyzico, Sipay, Param**) ile çalışan e-ticaret siteleri, pazaryerleri ve SaaS platformları için geliştirilmiş **Webhook / IPN Callback Bildirim Simülatörü, HMAC-SHA256 Token Doğrulayıcısı ve Mock Test Sunucusu**.

Karttan para çekilip siparişin askıda kalması, bildirim URL hataları ve valör/komisyon hesaplamalarıyla ilgili derinlemesine teknik rehberler için [Sanal POS & E-Ticaret Rehberi (eticaretokulu.com.tr)](https://eticaretokulu.com.tr) portalını inceleyebilirsiniz.

---

## 🎯 Hangi Sorunu Çözer?

E-ticaret geliştirmelerinde en sık karşılaşılan kriz: **Müşterinin kredi kartından provizyon alınması ancak backend'in webhook bildirimini işleyememesi ve siparişin "Ödeme Bekleniyor" olarak askıda kalmasıdır.**

Bu araç sayesinde:
1. Gerçek kredi kartı ile canlı veya sandbox çekim yapmaya gerek kalmadan backend bildirim ucunuza (`/api/payment/callback`) saniyeler içinde geçerli HMAC-SHA256 imzalı POST isteği fırlatabilirsiniz.
2. Sitenizin bankaya `HTTP 200 OK` ve `"OK"` yanıtı dönüp dönmediğini test edebilirsiniz.
3. Lokalde çalışırken gelen webhook paketlerini incelemek için mini mock dinleyici sunucusu açabilirsiniz.

---

## ✨ Özellikler

* 🛡️ **PayTR HMAC-SHA256 Token Algoritması:** `merchant_oid`, `merchant_salt`, `status` ve kuruş cinsinden `total_amount` birleşimiyle tam uyumlu PayTR hash'i üretir ve doğrular.
* 💳 **İyzico İmzası (Signature) & Token Simülasyonu:** İyzico Checkout Form ve bildirim akışlarını simüle eder.
* ⚡ **Sipay ve Param Entegrasyon Desteği:** Hash-key ve durum kodlarını (`status_code: 100`) otomatik paketler.
* 📡 **Test Gönderici (CLI Webhook Sender):** Yerel sunucunuza (`http://localhost:8000/webhook`) veya ngrok tünelinize tek komutla test isteği atar.
* 🎧 **Mock Dinleyici Sunucusu (Mock Receiver):** Gelen POST isteklerini terminalde renkli ve JSON formatında görüntüler.
* 🪶 **Sıfır Harici Bağımlılık:** Harici hiçbir paket gerektirmez; saf Python standart kütüphanesiyle çalışır.

---

## 🚀 Hızlı Başlangıç

### 1. Kurulum

```bash
git clone https://github.com/eimza-kep/turkiye-sanalpos-webhook-simulator.git
cd turkiye-sanalpos-webhook-simulator
```

### 2. Komut Satırı Kullanımı

#### A. Sitenize Sahte Başarılı PayTR Bildirimi Gönderin:
```bash
python -m sanalpos_simulator send \
    --gateway paytr \
    --url http://localhost:8000/api/paytr-callback \
    --order-id SIPARIS-1001 \
    --amount 250.0 \
    --status success \
    --salt test_salt_123 \
    --key test_key_456
```

#### B. Sitenize Başarısız (Yetersiz Bakiye) Ödeme Bildirimi Gönderin:
```bash
python -m sanalpos_simulator send \
    --gateway paytr \
    --url http://localhost:8000/api/paytr-callback \
    --order-id SIPARIS-1002 \
    --amount 100.0 \
    --status failed
```

#### C. Gelen Webhook'ları İncelemek İçin Lokal Dinleyici Başlatın:
```bash
python -m sanalpos_simulator listen --port 8080
```

---

## 🐍 Python Projelerinizde Kullanım

```python
from sanalpos_simulator import PayTRSimulator, IyzicoSimulator

# 1. PayTR Hash Doğrulama (Backend Kodunuzda)
post_params = {
    "merchant_oid": "SIP-123",
    "status": "success",
    "total_amount": "10000",
    "hash": "..."
}

is_valid = PayTRSimulator.verify_hash(
    post_data=post_params,
    merchant_salt="your_merchant_salt",
    merchant_key="your_merchant_key"
)

if is_valid:
    print("Sipariş onaylandı!")
else:
    print("Güvenlik ihlali: Geçersiz imza!")
```

---

## 📜 Lisans

Bu proje **MIT Lisansı** ile lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına göz atınız.
