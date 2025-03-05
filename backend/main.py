from fastapi import FastAPI, BackgroundTasks
from datetime import datetime
from DBOperator import DBOperator
from json import loads, dumps
from kafka import KafkaProducer, KafkaConsumer
import json
import threading

app = FastAPI()

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    key_serializer=lambda k: k.encode('utf-8'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@app.post("/publish/{topic}")
def publish(topic: str, data: dict):
    """
    Send JSON data to a Kafka topic.
    """
    key = data.get("ship_id", "unknown_ship")
    message = data.get("event", "No event provided")

    producer.send(topic, key=key, value=message)
    producer.flush()
    return {"status": "message published successfully"}

def consume_messages():
    """
    Kafka consumer that runs in the background.
    """
    consumer = KafkaConsumer(
        'maritime-events',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        key_deserializer=lambda k: k.decode('utf-8') if k else None,
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

    print("Kafka Consumer is listening for events...")
    for message in consumer:
        print(f"[Kafka] Received Event: {message.key} -> {message.value}")

consumer_thread = threading.Thread(target=consume_messages, daemon=True)
consumer_thread.start()

@app.get("/")
def welcome():
    """
    FastAPI Home Endpoint.
    """
    return {
        "Message": "Welcome to FastAPI with Kafka!",
        "Retrieved": datetime.now(),
    }
