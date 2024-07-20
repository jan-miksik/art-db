# Use Python 3.11 base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the dependency files
COPY pyproject.toml poetry.lock /app/

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install --no-dev

# Copy the application code
COPY . /app/

# Command to run the Django server
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
