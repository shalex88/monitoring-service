#!/bin/bash

APP_NAME="monitoring"

cleanup() {
    sudo rabbitmqctl trace_off
    sudo rabbitmqctl stop
}

# Trap signals to ensure cleanup is called on script termination
trap cleanup SIGINT SIGTERM EXIT

# Activate the virtual environment
. ./"${APP_NAME}"/bin/activate

# Start RabbitMQ server in the background
sudo rabbitmq-server &

sleep 5
sudo rabbitmqctl trace_on

wait