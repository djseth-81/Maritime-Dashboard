import asyncio
from kafka import KafkaConsumer
import json

connected_clients = set()
kafka_to_ws_queue = asyncio.Queue()

def get_consumer():
    return KafkaConsumer(
        'maritime-events',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='latest',
        enable_auto_commit=True,
        key_deserializer=lambda k: k.decode('utf-8') if k else None,
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

def kafka_consumer_thread(loop):
    consumer = get_consumer()
    print("### Kafka Bridge: Listening for Kafka messages (thread)...")
    for message in consumer:
        msg = {
            "topic": message.topic,
            "key": message.key,
            "value": message.value,
            "timestamp": message.timestamp
        }
        print("### Kafka Bridge: Queuing message for WS clients:", msg)
        asyncio.run_coroutine_threadsafe(kafka_to_ws_queue.put(msg), loop)

async def kafka_listener():
    loop = asyncio.get_running_loop()
    import threading
    threading.Thread(target=kafka_consumer_thread, args=(loop,), daemon=True).start()

    while True:
        msg = await kafka_to_ws_queue.get()
        await notify_clients(json.dumps(msg))

async def notify_clients(message: str):
    to_remove = set()
    for client in connected_clients:
        try:
            await client.send_text(message)
        except Exception as e:
            print(f"### Kafka Bridge: Error sending to client: {e}")
            to_remove.add(client)
    connected_clients.difference_update(to_remove)
