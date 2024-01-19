FROM python:3.12-slim
# # Base image

# # Install system dependencies
# RUN apt-get update && apt-get install -y \  
#   build-essential \
#   curl

# # Install Poetry
# RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 -

# # Add poetry to path  
# ENV PATH="${PATH}:/opt/poetry/bin"

# # Copy project dependency files
# COPY pyproject.toml ./

# # Install dependencies - now cached!
# RUN poetry config virtualenvs.create false \
#   && poetry install --no-interaction --no-ansi --no-root

# # Set work directory
# WORKDIR /app

# # # Install Poetry
# # RUN pip install poetry

# # # Copy pyproject.toml and poetry.lock file (if exists)
# # COPY pyproject.toml ./

# # Install dependencies
# RUN poetry install --no-interaction --no-ansi --no-root

# # Copy project
# COPY . .

# # Migrate database
# RUN python3 manage.py migrate 

# # Collect static
# # RUN python manage.py collectstatic --no-input 

# # Gunicorn config
# COPY gunicorn_conf.py ./

# # Ports
# EXPOSE 8000  

# # Start app  
# CMD ["gunicorn", "--config", "gunicorn_conf.py", "artist_registry.wsgi:application"]
