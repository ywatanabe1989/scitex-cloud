# syntax=docker/dockerfile:1.4
# ============================================
# SciTeX Cloud - Production Image
# ============================================
# Multi-stage build optimized for size, security, and cache efficiency

# ============================================
# Stage 1: Python Dependencies Builder
# ============================================
FROM python:3.11-slim AS python-builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv

# Copy requirements ONLY (maximizes cache - this rarely changes)
COPY requirements.txt .

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r requirements.txt && \
    uv pip install --system gunicorn==21.2.0 psycopg2-binary

# Install scitex from PyPI (production uses stable releases)
# Version pinned for stability - Complete toolkit with all features
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system "scitex[dl,ml,jupyter,neuro,web,scholar,writer,dev]==2.1.2"

# Install Playwright browsers
RUN --mount=type=cache,target=/root/.cache/ms-playwright \
    python -m playwright install chromium && \
    python -m playwright install-deps

# ============================================
# Stage 2: Node.js Tools Builder
# ============================================
FROM node:20-slim AS node-builder

# Install Mermaid CLI
RUN npm install -g @mermaid-js/mermaid-cli

# ============================================
# Stage 3: System Tools Builder
# ============================================
FROM alpine:latest AS tool-builder

# Install yq (YAML parser)
RUN YQ_VERSION=v4.44.3 && \
    YQ_BINARY=yq_linux_amd64 && \
    wget https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/${YQ_BINARY} -O /usr/local/bin/yq && \
    chmod +x /usr/local/bin/yq

# ============================================
# Stage 4: Runtime (Final Minimal Image)
# ============================================
FROM python:3.11-slim AS runtime

LABEL maintainer="ywatanabe@scitex.ai"
LABEL description="SciTeX Cloud - Production"
LABEL version="0.1.0-alpha"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    SCITEX_CLOUD_DJANGO_SETTINGS_MODULE=config.settings.settings_prod

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core runtime
    curl \
    netcat-openbsd \
    jq \
    git \
    # Database runtime library (not dev package)
    libpq5 \
    # LaTeX runtime
    texlive-latex-base \
    texlive-latex-extra \
    texlive-latex-recommended \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-bibtex-extra \
    texlive-science \
    texlive-pictures \
    texlive-plain-generic \
    # bibtex is included in texlive-bibtex-extra
    latexdiff \
    ghostscript \
    poppler-utils \
    # Image processing runtime
    imagemagick \
    # Browser runtime (Chromium for Mermaid/Playwright)
    chromium \
    fonts-liberation \
    # Playwright runtime libraries (minimal set)
    libglib2.0-0t64 \
    libnspr4 \
    libnss3 \
    libdbus-1-3 \
    libatk1.0-0t64 \
    libatk-bridge2.0-0t64 \
    libcups2t64 \
    libxcb1 \
    libxkbcommon0 \
    libatspi2.0-0t64 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libcairo2 \
    libpango-1.0-0 \
    libasound2t64 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder (avoids rebuilding)
COPY --from=python-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-builder /usr/local/bin /usr/local/bin
# Copy Playwright cache if it exists (use wildcard to avoid failure if missing)
COPY --from=python-builder /root/.cache/ms-playwright* /root/.cache/

# Copy Node.js and Mermaid from node-builder
COPY --from=node-builder /usr/local/bin/node /usr/local/bin/node
COPY --from=node-builder /usr/local/bin/npm /usr/local/bin/npm
COPY --from=node-builder /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/@mermaid-js/mermaid-cli/src/cli.js /usr/local/bin/mmdc && \
    chmod +x /usr/local/bin/mmdc

# Copy yq from tool-builder
COPY --from=tool-builder /usr/local/bin/yq /usr/local/bin/yq

# Configure ImageMagick (PDF policy) - check if file exists first
RUN if [ -f /etc/ImageMagick-6/policy.xml ]; then \
        sed -i 's/<policy domain="coder" rights="none" pattern="PDF" \/>/<policy domain="coder" rights="read|write" pattern="PDF" \/>/g' /etc/ImageMagick-6/policy.xml || true; \
    fi

# Create non-root user and directories
RUN useradd -m -u 1000 scitex && \
    mkdir -p /app/staticfiles /app/media /app/logs /app/run /app/.cache/containers && \
    chown -R scitex:scitex /app

# Copy application code (last - changes most frequently)
COPY --chown=scitex:scitex . .


# Copy prod-specific entrypoint
COPY --chown=scitex:scitex deployment/docker/docker_prod/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to non-root user for security
USER scitex

# Verify critical tools (fail fast)
RUN pdflatex --version && \
    bibtex --version && \
    convert --version && \
    yq --version && \
    python --version && \
    echo "✅ Production image verified"

# ============================================
# Runtime Configuration
# ============================================

HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--threads", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]

# EOF
