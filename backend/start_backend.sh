#!/bin/bash

RUNTIME_ARG=$1
echo "Runtime Argument: $RUNTIME_ARG"

set -e

TARGET_DIR=/data/builds

# Ensure Logging Directory Exists
mkdir -p /mnt/logs

# If Rebuild
if [[ "$REBUILD_DB" =~ ^([yY][eE][sS]|[yY])$ ]]; then
  # Unzip The Data
  mkdir -p $TARGET_DIR
  # unzip -o /mnt/data/build.zip -d $TARGET_DIR

  # Setup Backend
  python3 setup_db.py --data $TARGET_DIR --rebuild --bundle $DATA_BUNDLE
fi

# If Run PyTests
if [[ "$RUN_TESTS" =~ ^([yY][eE][sS]|[yY])$ ]]; then
  python3 -m pytest tests/ -vv
fi

# Start Server
# python3 server.py
gunicorn --timeout 300 --workers 5 --log-level 'debug' --bind 0.0.0.0:5000 $RUNTIME_ARG server:app 
