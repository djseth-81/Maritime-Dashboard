from pprint import pprint
import msgpack
from fastapi import FastAPI
from kafka import KafkaConsumer, TopicPartition

app = FastAPI()

# https://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html
consumer = KafkaConsumer("books", bootstrap_servers='localhost:9092')
# param group_id str : specifies groupID for dynamic partition assignment

# Can manually assign partitions
# consumer.assign([TopicPartition("foobar",2)])
# msg = next(consumer) # Guesing this pulls the NEXT MESSAGE sent to assigned topic partition

# TODO:
# Handle <Ctrl-C>

metrics = consumer.metrics() # Get consumer metrics

pprint(metrics)

for msg in consumer: # Runs until <Ctrl-C>
    pprint(msg)
    pprint(msg.headers) # Access record header info as list of tuples

# The following apparently deserializes msgpack-encoded values
# consumer = KafkaConsumer("books", bootstrap_servers='localhost:9092', value_deserializer=msgpack.loads) # Trying to use this throws errors?
# consumer.subscribe(["books"]) # Assigns consumer to topic
# for msg in consumer:
#     assert isinstance(msg.value, dict)
