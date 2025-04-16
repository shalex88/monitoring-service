#!/bin/bash

APP_NAME="monitoring"

sudo apt install python3-venv -y && \
# sudo sudo pip3 install -U jetson-stats && \
sudo apt install rabbitmq-server && \
sudo systemctl disable rabbitmq-server && \
sudo sudo rabbitmqctl stop && \
python3 -m venv "${APP_NAME}" && \
. ./"${APP_NAME}"/bin/activate && \
pip install -r dependencies.txt