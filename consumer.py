from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "orders",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",   # Consumer'ın daha önce gönderilmiş mesajları da okuyabilmesini sağlı
    group_id="test-group"
)

print("Kafka dinleniyor...")

for message in consumer:
    print("Gelen mesaj:", message.value.decode())