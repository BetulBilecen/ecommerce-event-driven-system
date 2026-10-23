# Kafkaya mesaj gönderecek taraf
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

order_event = {
    "event": "OrderCreated",
    "order_id": 1,
    "product_id": 5,
    "quantity": 2
}

producer.send(
    "orders",
    order_event
)

producer.flush()

print("Sipariş eventi gönderildi!")