FROM python:3.11-slim

# Install system dependencies required for Playwright and other native extensions
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (needed for the scrapers)
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy the rest of the application
COPY . .

# Expose API port
EXPOSE 8000

# We use the Procfile for execution commands in PaaS environments,
# but for Docker compose or raw docker, we can set a default CMD
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "backend.main:app", "--bind", "0.0.0.0:8000"]
