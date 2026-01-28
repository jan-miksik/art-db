# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Collect static files at build time (Django admin CSS/JS)
# Uses dummy values for required env vars since we only need staticfiles
RUN DJANGO_SECRET_KEY=build-only-dummy-key \
    ARWEAVE_WALLET_B64=$(echo '{}' | base64) \
    python manage.py collectstatic --noinput

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Expose port
EXPOSE 8000

# Use entrypoint script which handles wallet setup and migrations
# The entrypoint.sh script will:
# 1. Materialize Arweave wallet from ARWEAVE_WALLET_B64 env var
# 2. Run database migrations
# 3. Execute the CMD (gunicorn)
ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "artist_registry.wsgi:application", "--config", "gunicorn_conf.py"]
