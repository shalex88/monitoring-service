import pika
import json
from datetime import datetime
import threading
import time
import sqlite3

rabbitmq_host = 'localhost'
exchange_name = 'camera_stats'

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()

# Declare the exchange
channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

# Create a temporary queue for this subscriber
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# Bind the queue to the exchange
channel.queue_bind(exchange=exchange_name, queue=queue_name)

print("Waiting for messages. To exit, press CTRL+C")

# Data structure to store messages for the current second
current_data_store = {
    "camA": {"zoom": "N/A", "focus": "N/A"},
    "camB": {"zoom": "N/A", "focus": "N/A"}
}
data_lock = threading.Lock()  # Lock to synchronize access to current_data_store
current_second = None  # Track the current second being processed

def init_db():
    # Initialize SQLite database
    conn = sqlite3.connect(exchange_name + '.db')  # Creates a file-based SQLite database
    cursor = conn.cursor()

    # Create a table to store stats
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp INTEGER,
        camA_zoom INTEGER,
        camA_focus INTEGER,
        camB_zoom INTEGER,
        camB_focus INTEGER
    )
    ''')
    conn.commit()
    return conn


def save_to_database(conn, data):
    """Save data to the SQLite database."""
    print(f"Saving to database: {data}")
    cursor = conn.cursor()

    timestamp = list(data.keys())[0]
    camA = data[timestamp]["camA"]
    camB = data[timestamp]["camB"]
    cursor.execute('''
        INSERT INTO stats (timestamp, camA_zoom, camA_focus, camB_zoom, camB_focus)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, camA["zoom"], camA["focus"], camB["zoom"], camB["focus"]))
    conn.commit()

def save_data(conn):
    """Finalize and save the data for the current second."""
    global current_second, current_data_store
    with data_lock:
        if current_second:
            # Save the finalized data to the database
            save_to_database(conn, {datetime.now().isoformat(): current_data_store})
        # Move to the next second
        current_second = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Reset the data store for the new second
        current_data_store = {
            "camA": {"zoom": "N/A", "focus": "N/A"},
            "camB": {"zoom": "N/A", "focus": "N/A"}
        }

def periodic_data_saver():
    db = init_db()
    while True:
        save_data(db)
        time.sleep(1)

def message_received_callback(ch, method, properties, body):
    """Update the data for the current second based on the received message."""
    global current_second, current_data_store
    # Parse the JSON message
    message = json.loads(body.decode())
    topic = message.get("topic")
    zoom = message.get("zoom")
    focus = message.get("focus")

    # Prepare the data for the topic
    topic_data = {
        "zoom": zoom,
        "focus": focus
    }

    with data_lock:
        # Ensure the current second is initialized
        if not current_second:
            current_second = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Update the data for the current second
        current_data_store[topic] = topic_data

if __name__ == "__main__":
    # Start the periodic data saver in a separate thread
    threading.Thread(target=periodic_data_saver, daemon=True).start()

    # Start consuming messages
    channel.basic_consume(queue=queue_name, on_message_callback=message_received_callback, auto_ack=True)
    channel.start_consuming()