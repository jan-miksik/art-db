#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Start Docker containers
docker compose up -d


# Run Django server
python3 manage.py runserver