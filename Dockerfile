# GIST Framework Docker Image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libc-dev \
    libffi-dev \
    libssl-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package in development mode
RUN pip install -e .

# Create non-root user for security
RUN groupadd -r gist && useradd -r -g gist gist
RUN chown -R gist:gist /app
USER gist

# Create directories for data and logs
RUN mkdir -p /app/data /app/logs /app/outputs

# Expose port for API (if using FastAPI)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import gist_calculator; print('OK')" || exit 1

# Default command - run demo
CMD ["python", "gist_calculator.py", "--demo"]

# Labels for metadata
LABEL maintainer="GIST Framework Research Team" \
      version="1.0.0" \
      description="GIST Framework for Digital Maturity Assessment in Italian Retail Sector" \
      org.opencontainers.image.title="GIST Framework" \
      org.opencontainers.image.description="Framework per la Valutazione della Maturità Digitale nel settore GDO" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="GIST Framework Research Team" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/your-org/gist-framework"