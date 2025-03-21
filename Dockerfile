# Build arguments
ARG PYTHON_VERSION=3.11-slim

FROM python:${PYTHON_VERSION}

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# Ensure Python output is sent directly to the terminal (unbuffered)
ENV PYTHONUNBUFFERED 1

# Install uv globally
RUN pip install --no-cache-dir -U uv

# Copy all necessary files (including lockfile and project definition)
COPY pyproject.toml uv.lock ./
COPY ./app /app

# Install project using uv.lock implicitly
RUN uv pip install --system --no-cache-dir .

# Install dos2unix
RUN apt-get update && apt-get install -y dos2unix

# Copy remaining files
COPY ./scripts ./
COPY ./migrations /migrations
COPY ./compose-entrypoint.sh /compose-entrypoint.sh

# Fix potential file issues
RUN dos2unix /compose-entrypoint.sh

# Grant execution permissions
RUN chmod +x /compose-entrypoint.sh

# Entrypoint
ENTRYPOINT ["sh", "compose-entrypoint.sh"]
