FROM cgr.dev/chainguard/python:latest-dev AS builder

# Define version argument with default from setup.py
ARG VERSION=1.0.3
LABEL org.opencontainers.image.version="${VERSION}"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set up application directory
WORKDIR /app

# Copy requirements first to leverage caching
COPY requirements.txt .

# Create a virtual environment and install dependencies
RUN python -m venv /app/.venv && \
    . /app/.venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Use the minimal runtime image for the final stage
FROM cgr.dev/chainguard/python:latest

# Set up non-root user
USER nonroot:nonroot
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/.venv" \
    PYTHONPATH="/app"

# Copy over virtual environment and application code
COPY --from=builder --chown=nonroot:nonroot /app/.venv /app/.venv
COPY --chown=nonroot:nonroot devkit/ /app/devkit/
COPY --chown=nonroot:nonroot setup.py pyproject.toml README.md /app/

# Add metadata
ARG VERSION=1.0.3
ARG BUILD_DATE
ARG VCS_REF

LABEL org.opencontainers.image.title="DevKit" \
    org.opencontainers.image.description="Development workflow automation tool" \
    org.opencontainers.image.version="${VERSION}" \
    org.opencontainers.image.created="${BUILD_DATE}" \
    org.opencontainers.image.authors="Philip Walsh <spaghetticodemedia@gmail.com>" \
    org.opencontainers.image.url="https://github.com/Philip-Walsh/devkit" \
    org.opencontainers.image.source="https://github.com/Philip-Walsh/devkit" \
    org.opencontainers.image.revision="${VCS_REF}" \
    org.opencontainers.image.licenses="MIT"

# Define entrypoint and default command
ENTRYPOINT ["python", "-m", "devkit.cli"]
CMD ["--help"]

# Define a simple health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD python -m devkit.cli version current || exit 1 