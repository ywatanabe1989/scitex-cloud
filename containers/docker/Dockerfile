# SciTeX Cloud - Docker Image
FROM python:3.11-slim

# Metadata
LABEL maintainer="ywatanabe@scitex.ai"
LABEL description="SciTeX Cloud - Research Collaboration Platform"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Working directory
WORKDIR /app

# System dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn==21.2.0 psycopg2-binary

# Copy application
COPY . .

# Run as non-root user for security
RUN useradd -m -u 1000 scitex && \
    chown -R scitex:scitex /app

# Create directories for static files, media, and logs (after changing ownership)
RUN mkdir -p staticfiles media logs/uwsgi run && \
    chown -R scitex:scitex staticfiles media logs run

USER scitex

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--threads", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
