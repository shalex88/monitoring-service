#!/usr/bin/env python3

import time
import pika
import json
from datetime import datetime
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="RabbitMQ Publisher")
parser.add_argument("--topic", required=True, help="Topic name for the message")
parser.add_argument("--sleep", required=True, help="Sleep time in seconds between messages")
args = parser.parse_args()

# RabbitMQ connection parameters
rabbitmq_host = 'localhost'
exchange_name = 'camera_stats'

# Establish connection to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()

# Declare an exchange for Pub/Sub
channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

try:
    while True:
        zoom = 3
        focus = 5
        iso_timestamp = datetime.now().isoformat()  # Generate ISO8601 timestamp

        # Create a JSON message
        message = {
            "topic": args.topic,
            "zoom": zoom,
            "focus": focus,
            "timestamp": iso_timestamp
        }

        # Convert the message to a JSON string
        message_body = json.dumps(message)

        # Publish the message to the exchange
        properties = pika.BasicProperties(
            content_type='application/json',  # Indicate the message format
        )
        channel.basic_publish(exchange=exchange_name, routing_key='', body=message_body, properties=properties)
        print(f"Sent message: {message_body}")
        time.sleep(int(args.sleep))
except KeyboardInterrupt:
    print("Interrupted by user.")
finally:
    # Close the connection when done
    connection.close()
    print("Connection to RabbitMQ closed.")