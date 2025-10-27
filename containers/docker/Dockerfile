# SciTeX Cloud - Docker Image
FROM python:3.11-slim

# Metadata
LABEL maintainer="ywatanabe@scitex.ai"
LABEL description="SciTeX Cloud - Research Collaboration Platform"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_SYSTEM_PYTHON=1

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

# Install uv for faster package installation
# UV installer installs to /root/.local/bin by default
# We move binaries to /usr/local/bin for system-wide access
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    mv /root/.local/bin/uvx /usr/local/bin/uvx && \
    chmod 755 /usr/local/bin/uv /usr/local/bin/uvx && \
    uv --version

# Copy Python dependencies and install with uv (much faster than pip)
# Use cache mount for uv to speed up rebuilds
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r requirements.txt && \
    uv pip install --system gunicorn==21.2.0 psycopg2-binary

# Copy application
COPY . .

# Create non-root user for security (after uv is installed system-wide)
RUN useradd -m -u 1000 scitex && \
    chown -R scitex:scitex /app && \
    chown -R scitex:scitex /usr/local/lib/python3.11/site-packages && \
    chown -R scitex:scitex /usr/local/bin && \
    mkdir -p /usr/local/share/man/man1 /usr/local/etc/jupyter && \
    chown -R scitex:scitex /usr/local/share /usr/local/etc && \
    chmod -R u+w /usr/local/lib/python3.11/site-packages && \
    chmod -R u+w /usr/local/bin && \
    chmod -R u+w /usr/local/share && \
    chmod -R u+w /usr/local/etc

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
