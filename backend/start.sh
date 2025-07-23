#!/bin/bash

echo "Waiting for database..."
python init_db.py

echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 8000 