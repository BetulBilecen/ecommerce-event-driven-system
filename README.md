# E-Commerce Event System

Kafka tabanlı, olay güdümlü (*event-driven*) bir e-ticaret backend projesi. FastAPI ile ürün ve sipariş işlemleri sunulur; PostgreSQL verileri saklar, Redis ürün listesini önbelleğe alır ve Apache Kafka sipariş ile stok sonuçlarını servisler arasında asenkron olarak iletir.

> **Proje durumu:** Öğrenme ve geliştirme amaçlı bir prototiptir; üretim ortamında kullanılmaya hazır değildir. Bu README, mevcut Python dosyalarının yapısına göre hazırlanmıştır. Docker Compose ve NGINX yapılandırmaları henüz projede bulunmadığı için Docker üzerinden tek komutla kurulum yapıldığı varsayılmamıştır.

## İçindekiler

- [Özellikler](#özellikler)
- [Mimari ve Sipariş Akışı](#mimari-ve-sipariş-akışı)
- [Kullanılan Teknolojiler](#kullanılan-teknolojiler)
- [Proje Yapısı](#proje-yapısı)
- [Gereksinimler](#gereksinimler)
- [Kurulum ve Çalıştırma](#kurulum-ve-çalıştırma)
- [API Uç Noktaları](#api-uç-noktaları)
- [Örnek İstekler](#örnek-istekler)
- [Bilinen Sınırlamalar ve Geliştirme Alanları](#bilinen-sınırlamalar-ve-geliştirme-alanları)

## Özellikler

- FastAPI ile REST API geliştirme
- SQLAlchemy ORM üzerinden PostgreSQL ile veri işlemleri
- Redis ile ürün listesini önbelleğe alma
- Apache Kafka ile sipariş ve stok olaylarını asenkron iletme
- Stok kontrolü ve stok sonucuna göre sipariş durumunu güncelleme
- Stok sonuçlarını konsola bildiren notification servisi

## Mimari ve Sipariş Akışı

```text
Client
  |
  v
FastAPI (main.py)
  |                         \
  v                          v
PostgreSQL                  Redis
  |
  | OrderCreated
  v
Kafka topic: orders
  |
  v
Inventory Service
  |                       |
  | stok yeterli          | stok yetersiz
  v                       v
StockUpdated          StockRejected
  \                       /
   \                     /
    v                   v
    Kafka topic: inventory-events
               |
       +-------+--------+
       |                |
       v                v
Order Status       Notification
Service             Service
       |
       v
Order status: confirmed / failed
```

### Sipariş akışı

1. İstemci `POST /orders` isteği gönderir.
2. API, ürünün varlığını ve satışa açık olup olmadığını kontrol eder.
3. Sipariş PostgreSQL'e `pending` durumuyla kaydedilir.
4. `OrderCreated` olayı Kafka'daki `orders` topic'ine gönderilir.
5. `inventory_service.py` olayı tüketir ve ürünün stok miktarını kontrol eder.
6. Stok yeterliyse stok azaltılır ve `StockUpdated` olayı `inventory-events` topic'ine gönderilir.
7. Stok yeterli değilse `StockRejected` olayı gönderilir.
8. `order_status_service.py`, sipariş durumunu `confirmed` veya `failed` olarak günceller.
9. `notification_service.py`, stok sonucunu konsola yazdırır.

Örnek `OrderCreated` olayı:

```json
{
  "event": "OrderCreated",
  "order_id": 1,
  "product_id": 5,
  "quantity": 2
}
```

Örnek stok sonucu olayı:

```json
{
  "event": "StockUpdated",
  "order_id": 1,
  "product_id": 5,
  "quantity": 2
}
```

Stok yetersiz olduğunda `event` alanı `StockRejected` olur.

## Kullanılan Teknolojiler

| Teknoloji | Kullanım amacı |
|---|---|
| Python | Backend ve servis geliştirme |
| FastAPI | REST API |
| Pydantic | İstek ve yanıt verilerinin doğrulanması |
| SQLAlchemy | ORM ve veritabanı işlemleri |
| PostgreSQL | Kalıcı veri saklama |
| Apache Kafka | Asenkron olay iletimi |
| Redis | Ürün listesi önbelleği |
| Docker | Bağımlı servisleri konteynerlerde çalıştırmak için planlanan ortam |

## Proje Yapısı

```text
ecommerce-event-system/
├── consumer.py               # orders topic'ini dinleyen basit test consumer'ı
├── database.py               # PostgreSQL bağlantısı ve SQLAlchemy oturumu
├── inventory_service.py      # Stok kontrolü ve stok güncelleme
├── kafka_producer.py         # API'nin kullandığı sipariş event producer'ı
├── main.py                   # FastAPI uygulaması ve API uç noktaları
├── models.py                 # Product ve Order SQLAlchemy modelleri
├── notification_service.py   # Stok sonuçlarını konsola yazdırır
├── order_status_service.py   # Sipariş durumunu günceller
├── producer.py               # Örnek Kafka mesajı gönderen test dosyası
├── redis_client.py           # Redis bağlantısı
├── schemas.py                # Pydantic istek/yanıt şemaları
├── .env                      # Yerel ortam değişkenleri (Git'e eklenmemeli)
├── .gitignore
└── README.md
```

> `venv/` klasörünü GitHub'a yüklemeyin. `.env` dosyasını da repoya eklemeyin; gizli değerler için `.gitignore` kullanın.

## Gereksinimler

- Python 3.10 veya üzeri
- PostgreSQL
- Apache Kafka
- Redis

Gerekli Python paketleri:

- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `psycopg2-binary`
- `pydantic`
- `kafka-python`
- `redis`

## Kurulum ve Çalıştırma

### 1. Repoyu klonlayın

```bash
git clone https://github.com/GITHUB_KULLANICI_ADIN/ecommerce-event-driven-system.git
cd ecommerce-event-driven-system
```

`GITHUB_KULLANICI_ADIN` kısmını GitHub kullanıcı adınızla değiştirin.

### 2. Sanal ortam oluşturun

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Paketleri kurun:

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic kafka-python redis
```

### 3. Bağımlı servisleri hazırlayın

PostgreSQL, Kafka ve Redis'in çalışır durumda olması gerekir. Mevcut kodda bağlantılar aşağıdaki adresleri kullanıyor:

| Servis | Kodda kullanılan adres |
|---|---|
| PostgreSQL | `localhost:15432`, veritabanı `ecommerce_db` |
| Kafka | `localhost:9092` |
| Redis | `localhost:6379` |

**Güvenlik notu:** Veritabanı bağlantı bilgilerini doğrudan `database.py` içinde tutmak yerine `.env` dosyasından veya ortam değişkenlerinden okuyacak şekilde yapılandırın. Gerçek parolaları GitHub'a göndermeyin.

> Projede şu anda Docker Compose yapılandırması bulunmadığından bu servislerin nasıl başlatılacağı mevcut yerel kurulumunuza bağlıdır. Docker desteği eklendiğinde bu bölüm güncellenebilir.

### 4. Servisleri ayrı terminallerde çalıştırın

Önce PostgreSQL, Kafka ve Redis'in çalıştığından emin olun. Ardından proje kök dizininde aşağıdaki Python dosyalarını ayrı terminallerde başlatın.

**Terminal 1 — FastAPI**

```bash
uvicorn main:app --reload
```

**Terminal 2 — Inventory Service**

```bash
python inventory_service.py
```

**Terminal 3 — Order Status Service**

```bash
python order_status_service.py
```

**Terminal 4 — Notification Service**

```bash
python notification_service.py
```

`consumer.py` ve `producer.py`, Kafka akışını elle test etmek için yardımcı dosyalardır; normal sipariş akışında çalıştırılmaları zorunlu değildir.

### 5. API dokümantasyonunu açın

FastAPI çalışırken:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Uç Noktaları

| Metot | Uç nokta | Açıklama |
|---|---|---|
| `GET` | `/` | API'nin çalıştığını kontrol eder |
| `GET` | `/products` | Ürünleri Redis önbelleğinden veya PostgreSQL'den getirir |
| `POST` | `/products` | Yeni ürün oluşturur |
| `POST` | `/orders` | Sipariş oluşturur ve Kafka'ya `OrderCreated` olayı gönderir |
| `GET` | `/orders` | Siparişleri listeler |

## Örnek İstekler

### Ürün oluşturma

`POST /products`

```json
{
  "name": "Kablosuz Kulaklık",
  "description": "Bluetooth kablosuz kulaklık",
  "price": 1299.90,
  "stock": 20,
  "category": "Elektronik",
  "brand": "Example",
  "image_url": "https://example.com/headphones.jpg",
  "is_active": true
}
```

### Sipariş oluşturma

`POST /orders`

```json
{
  "product_id": 1,
  "quantity": 2
}
```

Stok kontrolü Kafka tüketicisi tarafından asenkron yapıldığı için ilk API yanıtında sipariş durumu `pending` olabilir. İşlem tamamlandıktan sonra `GET /orders` üzerinden güncel durumu kontrol edebilirsiniz.

## Bilinen Sınırlamalar ve Geliştirme Alanları

1. **Stok eşzamanlılığı:** Aynı ürüne aynı anda gelen siparişlerde yarış koşulları oluşabilir. Stok azaltma işlemi atomik bir veritabanı güncellemesi veya uygun transaction/kilit mekanizmasıyla güvenceye alınmalıdır.
2. **Tekrarlanan olaylar:** Kafka mesajları yeniden işlenebilir. Stok azaltma ve sipariş durumu güncelleme işlemlerine idempotency kontrolü eklenmelidir.
3. **Sipariş kaydı ve olay gönderimi:** Sipariş veritabanına kaydedildikten sonra Kafka gönderimi başarısız olursa sipariş `pending` kalabilir. Transactional outbox yaklaşımı bu riski azaltabilir.
4. **Redis önbelleği:** Yeni ürün eklendiğinde de `products` önbelleği temizlenmelidir; aksi hâlde eski liste dönebilir.
5. **Veri doğrulama:** `quantity` için pozitif sayı ve `price` için uygun alt sınır doğrulamaları eklenmelidir.
6. **Veritabanı ilişkileri:** `Order.product_id` için `ForeignKey("products.id")` kullanılması veri tutarlılığını güçlendirir.
7. **Parasal alanlar:** Fiyat ve toplam tutar için `Float` yerine `Numeric`/`Decimal` tercih edilmelidir.
8. **Hata yönetimi:** Veritabanı oturumları güvenli şekilde kapatılmalı; Kafka bağlantı ve gönderim hataları ele alınmalıdır.
9. **Yapılandırma ve güvenlik:** Parolalar ve servis adresleri ortam değişkenlerinden okunmalı; `.env` Git'e eklenmemelidir.
10. **Docker ve NGINX:** Servisleri tek komutla çalıştırmak ve istekleri ters vekil üzerinden yönlendirmek için Docker Compose ve NGINX yapılandırmaları ayrıca eklenebilir.
11. **Testler ve loglama:** API testleri, stok sınır durumları, tekrar eden olay testleri ve yapılandırılmış loglar eklenebilir.

---

Bu proje; **event-driven mimariyi**, **Apache Kafka ile asenkron mesajlaşmayı**, **Redis önbelleklemesini** ve **FastAPI ile backend geliştirmeyi** uygulamalı olarak öğrenmek amacıyla geliştirilmiştir.
