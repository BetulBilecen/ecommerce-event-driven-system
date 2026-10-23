from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)



# Partition seçimini kendisi otomatik yapar.
def send_order_event(order_event):
    future = producer.send(
        "orders",
        value=order_event
    )

    record_metadata = future.get(timeout=10) # Gönderim sonucunu bekler.

    print("Mesaj gönderildi.")
    print("Topic:", record_metadata.topic)
    print("Partition:", record_metadata.partition)  # Mesaj hangi partitonda
    print("Offset:", record_metadata.offset)

