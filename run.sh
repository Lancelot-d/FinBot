#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

echo "Running chromadb_adapter..."
python3 -m api_adapter.chromadb_adapter

echo "Starting the server..."
gunicorn -w 1 --timeout 360 --bind 0.0.0.0:8070 app:server