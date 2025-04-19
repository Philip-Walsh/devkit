FROM python:3.9-slim

LABEL maintainer="Philip Walsh <philip.walsh@example.com>"
LABEL org.opencontainers.image.source="https://github.com/Philip-Walsh/devkit"
LABEL org.opencontainers.image.description="DevKit - Development workflow automation tool"
LABEL org.opencontainers.image.licenses="MIT"

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Install the package
RUN pip install --no-cache-dir -e .

# Create a non-root user to run the application
RUN addgroup --system app && \
    adduser --system --group app

# Change ownership of the application files
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Set entrypoint
ENTRYPOINT ["devkit"]

# Default command
CMD ["--help"] 