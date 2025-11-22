# syntax=docker/dockerfile:1.4
# ============================================
# SciTeX Cloud - Development Image
# ============================================
# Optimized for cache efficiency and fast rebuilds

FROM python:3.11-slim

LABEL maintainer="ywatanabe@scitex.ai"
LABEL description="SciTeX Cloud - Development Environment"

# ============================================
# Environment Variables
# ============================================
# Set first - rarely changes

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=0 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

# ============================================
# System Dependencies
# ============================================
# Ordered by update frequency (least to most)
# Large, stable packages first for maximum cache reuse

RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core build tools (rarely change)
    build-essential \
    git \
    wget \
    curl \
    unzip \
    netcat-openbsd \
    openssh-client \
    jq \
    # Database (rarely change)
    libpq-dev \
    # LaTeX suite (large, rarely change - install early for caching)
    # Writer Dependencies
    texlive-latex-base \
    texlive-latex-extra \
    texlive-latex-recommended \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-science \
    texlive-publishers \
    texlive-luatex \
    texlive-xetex \
    texlive-bibtex-extra \
    texlive-pictures \
    texlive-plain-generic \
    texlive-lang-european \
    texlive-lang-english \
    texlive-extra-utils \
    latexdiff \
    latexmk \
    chktex \
    ghostscript \
    poppler-utils \
    perl \
    parallel \
    # Image processing
    imagemagick \
    # Browser automation dependencies
    chromium \
    chromium-driver \
    fonts-liberation \
    # Playwright runtime dependencies
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
    python3-bibtexparser \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# Tool Installation
# ============================================
# Install external tools - cached unless versions change

# Install uv (fast package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    mv /root/.local/bin/uvx /usr/local/bin/uvx && \
    chmod 755 /usr/local/bin/uv /usr/local/bin/uvx

# Install yq (YAML parser for scitex.writer)
RUN YQ_VERSION=v4.44.3 && \
    YQ_BINARY=yq_linux_amd64 && \
    wget https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/${YQ_BINARY} -O /usr/local/bin/yq && \
    chmod +x /usr/local/bin/yq

# Install inotify-tools (lightweight file watcher for template hot reload)
RUN apt-get update && apt-get install -y --no-install-recommends inotify-tools && rm -rf /var/lib/apt/lists/*

# Install Node.js and Mermaid CLI
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g @mermaid-js/mermaid-cli && \
    rm -rf /var/lib/apt/lists/*

# Configure ImageMagick (remove PDF security restrictions)
RUN if [ -f /etc/ImageMagick-6/policy.xml ]; then \
        sed -i 's/<policy domain="coder" rights="none" pattern="PDF" \/>/<policy domain="coder" rights="read|write" pattern="PDF" \/>/g' /etc/ImageMagick-6/policy.xml; \
    elif [ -f /etc/ImageMagick-7/policy.xml ]; then \
        sed -i 's/<policy domain="coder" rights="none" pattern="PDF" \/>/<policy domain="coder" rights="read|write" pattern="PDF" \/>/g' /etc/ImageMagick-7/policy.xml; \
    else \
        echo "⚠️  ImageMagick policy.xml not found, skipping PDF policy update"; \
    fi

# ============================================
# Python Dependencies
# ============================================
# Copy requirements first - changes less than app code

# Copy only requirements.txt (layer cached until requirements change)
COPY requirements.txt .

# Install SciTeX Cloud Python dependencies with cache mount
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r requirements.txt

# Install Playwright browsers (must persist in image for runtime use)
# Note: We already have chromium and dependencies installed above,
# so we skip install-deps which tries to install Ubuntu packages on Debian
RUN python -m playwright install chromium

# ============================================
# Application Code
# ============================================
# Copy application last - changes most frequently

# Copy application code
COPY . .

# Copy dev-specific entrypoint and helper scripts
COPY deployment/docker/docker_dev/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    chmod +x /app/deployment/docker/docker_dev/watch_templates.sh 2>/dev/null || true

# Create directories
RUN mkdir -p staticfiles media logs run .cache/containers

# ============================================
# Verification
# ============================================
# Verify installations - fails fast if something is wrong

RUN pdflatex --version && \
    bibtex --version && \
    latexdiff --version && \
    convert --version && \
    mmdc --version && \
    yq --version && \
    echo "✅ All scitex.writer dependencies verified"

# ============================================
# Runtime Configuration
# ============================================

HEALTHCHECK --interval=10s --timeout=3s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
# Use Daphne (ASGI server) for WebSocket support (PTY terminal, collaborative editing, etc.)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]

# EOF
