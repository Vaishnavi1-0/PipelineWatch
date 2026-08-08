import os
import json
import asyncio
import logging
import pika
from dotenv import load_dotenv
load_dotenv()

from log_analyzer import analyze_failure
from models import init_db, save_failure

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [worker] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "worker.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("pipelinewatch.worker")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = "failure_analysis"

def process_message(ch, method, properties, body):
    event = json.loads(body)
    logger.info(f"Received event: {event['repo']} run {event['run_id']}")
    try:
        summary = asyncio.run(analyze_failure(event["repo"], event["run_id"]))
        save_failure(
            repo=event["repo"], run_id=event["run_id"],
            workflow_name=event["workflow_name"], run_url=event["run_url"],
            summary=summary,
        )
        logger.info(f"Saved analysis for run {event['run_id']}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Failed to process event: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    init_db()
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_message)
    logger.info("Worker started, waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
