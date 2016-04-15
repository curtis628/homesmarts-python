"""
homesmarts.messaging
~~~~~~~~~~~~~

This module contains all the reusable RabbitMQ messaging functionality
"""

import logging
import pika

RABBITMQ_HOST = 'localhost'
DASH_EXCHANGE = "dash_exchange"

logger = logging.getLogger(__name__)


def create_rabbitmq_channel():
    """Creates a direct RabbitMQ exchange and returns the channel."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.exchange_declare(exchange=DASH_EXCHANGE, type='direct')
    return channel


def publish_message(key, message):
    """Publishes 'message' using 'key' as the routing_key."""
    logger.debug("Publishing [message=%s] to [key=%s]", message, key)
    channel = create_rabbitmq_channel()
    channel.basic_publish(exchange=DASH_EXCHANGE, routing_key=key, body=message)
