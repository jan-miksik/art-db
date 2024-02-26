#!/bin/bash

# Start Docker containers
docker compose up -d

# Activate the virtual environment
source venv/bin/activate

# Run Django server
python3 manage.py runserver