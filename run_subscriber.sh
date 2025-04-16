#!/bin/bash

APP_NAME="monitoring"

. ./"${APP_NAME}"/bin/activate
python3 "${APP_NAME}.py"