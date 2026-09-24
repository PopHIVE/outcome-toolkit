#!/bin/bash

HOST_URL="http://<LOAD_TEST_HOST>"
NUM_USERS=${1:-100}

python3 -m locust -f tests/locustfile.py \
    --users ${NUM_USERS} \
    --spawn-rate 1 \
    --host ${HOST_URL} \
    --headless \
    --run-time 5m
