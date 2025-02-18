from kafka import KafkaConsumer

consumer = KafkaConsumer('some_topic')
# returns ConsumerRecords, which are simple
for msg in consumer:
    print(msg)
