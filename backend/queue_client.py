import os
import json
import pika
from dotenv import load_dotenv
load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "")
QUEUE_NAME = "failure_analysis"

def publish_failure_event(event: dict):
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=json.dumps(event),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
