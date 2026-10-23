
from kafka import KafkaConsumer, KafkaProducer
import json

from database import SessionLocal
from models import Product

from redis_client import redis_client


producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


consumer = KafkaConsumer(
    "orders",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="latest",  # Eski mesajları tutmayacak
    group_id="inventory-service"
)


print("Inventory Service çalışıyor...")


for message in consumer:
    try:
        order_event = json.loads(message.value.decode("utf-8"))

        print("Inventory Service event aldı:")
        print(order_event)

        db = SessionLocal()

        product = db.query(Product).filter(
            Product.id == order_event["product_id"]
        ).first()

        if not product:
            print("Ürün bulunamadı.")
            db.close()
            continue

        print("Ürün bulundu:", product.name)
        print("Mevcut stok:", product.stock)

        quantity = order_event["quantity"]

        if product.stock < quantity:
            print("Yeterli stok bulunmuyor.")

            inventory_event = {
                "event": "StockRejected",
                "order_id": order_event["order_id"],
                "product_id": order_event["product_id"],
                "quantity": quantity
            }

            producer.send(
                "inventory-events",
                inventory_event
            )

            producer.flush()

            print("StockRejected eventi gönderildi.")

            db.close()

            continue

        product.stock -= quantity

        db.commit()

        print("Yeni stok:", product.stock)

        # Redis güncelleme
        redis_client.delete("products")
        print("Products cache temizlendi.")

        inventory_event = {
            "event": "StockUpdated",
            "order_id": order_event["order_id"],
            "product_id": order_event["product_id"],
            "quantity": quantity
        }

        producer.send(
            "inventory-events",
            inventory_event
        )

        producer.flush()

        print("StockUpdated eventi gönderildi.")

        db.close()

    except json.JSONDecodeError:
        print("Geçersiz JSON mesajı, atlandı.")
