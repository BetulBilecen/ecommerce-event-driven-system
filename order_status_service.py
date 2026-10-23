
from kafka import KafkaConsumer
import json

from database import SessionLocal
from models import Order


consumer = KafkaConsumer(
    "inventory-events",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="latest",
    group_id="order-status-service"
)

print("Order Status Service çalışıyor...")


for message in consumer:
    try:
        inventory_event = json.loads(
            message.value.decode("utf-8")
        )

        print("\n---------------------\n")
        print("Inventory event alındı:")
        print(inventory_event)

        if inventory_event["event"] == "StockUpdated":
            new_status = "confirmed"

        elif inventory_event["event"] == "StockRejected":
            new_status = "failed"

        else:
            continue

        db = SessionLocal()

        order = db.query(Order).filter(
            Order.id == inventory_event["order_id"]
        ).first()

        if not order:
            print("Sipariş bulunamadı.")
            db.close()
            continue

        order.status = new_status

        db.commit()

        print(
            f"Sipariş {order.id} {new_status} olarak güncellendi."
        )

        db.close()

    except json.JSONDecodeError:
        print("Geçersiz JSON mesajı, atlandı.")
