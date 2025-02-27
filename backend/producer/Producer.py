from pprint import pprint
from fastapi import FastAPI
from datetime import datetime
from json import loads, dumps

from kafka import KafkaProducer
# https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html#kafkaproducer
# producer = KafkaProducer(bootstrap_servers='localhost:9092')
# Additional parameters
#   - compression_type: str
#       - gzip, LZ4, Snappy, Zstd

# # Just a raw set of bytes sent as is, no condom
# for _ in range(10):
#     producer.send('books', key=b'greet', value=b'HI!')
#     # topic _________|
      # Additional parameters for send
      #   - headers: list of tuples

# # Blocking message until timeout or pending messages are at least put on network
# # NOTE: doesn't guarantee delivery success, only useful for configuring internal batching
# future = producer.send('books', key=b'junk', value=b'another message')
# result = future.get(timeout=60) # Sends message after 60s timeout
# pprint(result)

# serealizing strings -> For some reason, TypeError!
# producer = KafkaProducer(bootstrap_servers='localhost:9092', 
#                          value_serializer=str.encode)
# future = producer.send('books', key='supersecret', value=b'12356543567654323456765432')
# result = future.get(timeout=60) # Sends message after 60s timeout
# pprint(result)

# serealizing JSON
producer = KafkaProducer(bootstrap_servers='localhost:9092', 
                         value_serializer=lambda v: dumps(v).encode('utf-8'))
future = producer.send('books', key=b'AHHHHHH', value={'foo': 'bar'})
result = future.get(timeout=60) # Sends message after 60s timeout
pprint(result)

