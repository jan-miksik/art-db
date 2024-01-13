# Base image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy pyproject.toml and poetry.lock file (if exists)
COPY pyproject.toml ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy project
COPY . .

# Migrate database
RUN python3 manage.py migrate 

# Collect static
# RUN python manage.py collectstatic --no-input 

# Gunicorn config
COPY gunicorn_conf.py ./

# Ports
EXPOSE 8000  

# Start app  
CMD ["gunicorn", "--config", "gunicorn_conf.py", "artist_registry.wsgi:application"]
