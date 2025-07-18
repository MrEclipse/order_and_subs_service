import os
import json
import pika

RABBIT_USER = os.getenv("RABBITMQ_USER")
RABBIT_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
RABBIT_HOST = os.getenv("RABBITMQ_HOST", "rabbit")
RABBIT_PORT = os.getenv("RABBITMQ_PORT", "5672")
RABBIT_VHOST = os.getenv("RABBITMQ_VHOST", "/")

RABBITMQ_URL = (
    f"amqp://{RABBIT_USER}:{RABBIT_PASSWORD}@"
    f"{RABBIT_HOST}:{RABBIT_PORT}{RABBIT_VHOST}"
)


def new_order_notification(telegram_id: str):
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue="orders_notifications", durable=True)

    payload = json.dumps({"telegram_id": telegram_id})

    channel.basic_publish(
        exchange="",
        routing_key="orders_notifications",
        body=payload,
        properties=pika.BasicProperties(delivery_mode=2))
    connection.close()
