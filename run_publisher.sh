#!/bin/bash

APP_NAME="monitoring"

. ./"${APP_NAME}"/bin/activate && \
./tests/publisher.py --topic $1 --sleep $2