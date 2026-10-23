from kafka import KafkaConsumer
import json


consumer = KafkaConsumer(
    "inventory-events",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="latest",
    group_id="notification-service"
)


print("Notification Service çalışıyor...")


for message in consumer:
    try:
        inventory_event = json.loads(
            message.value.decode("utf-8")
        )

        print("\n---------------------\n")
        print("Inventory event alındı:")
        print(inventory_event)

        if inventory_event["event"] == "StockUpdated":

            print(
                f"!! Bildirim: Sipariş #{inventory_event['order_id']} "
                f"başarıyla onaylandı."
            )

        elif inventory_event["event"] == "StockRejected":

            print(
                f"!! Bildirim: Sipariş #{inventory_event['order_id']} "
                f"stok yetersizliği nedeniyle başarısız oldu."
            )

    except json.JSONDecodeError:
        print("\n - Geçersiz JSON mesajı, atlandı.")