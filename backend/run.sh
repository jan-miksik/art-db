#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Start Docker containers
docker compose up -d

# Set Django settings module
export DJANGO_SETTINGS_MODULE=artist_registry.settings

# Run Django server
python3 manage.py runserver