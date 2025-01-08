# Build arguments
ARG PYTHON_VERSION=3.11-slim

FROM python:${PYTHON_VERSION}

# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONDONTWRITEBYTECODE
# Prevents Python from writing .pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1

# ensures that the python output is sent straight to terminal (e.g. your container log)
# without being first buffered and that you can see the output of your application (e.g. django logs)
# in real time. Equivalent to python -u: https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED 1

# Install virtualenv and create a virtual environment
RUN pip install --no-cache-dir -U poetry && \
    poetry config virtualenvs.create false

# Copy the poetry.lock and pyproject.toml files
# and install dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-interaction --no-ansi

# Install dos2unix
RUN apt-get update && apt-get install -y dos2unix


# Copy the project files into the working directory
COPY ./app /app
COPY ./scripts .
COPY ./data /data
COPY ./migrations /migrations
COPY ./compose-entrypoint.sh /compose-entrypoint.sh

RUN dos2unix /compose-entrypoint.sh

# Grant execution permissions
RUN chmod +x /compose-entrypoint.sh

# Inicializa banco, roda migrations e sobe servidor
ENTRYPOINT ["sh", "compose-entrypoint.sh"]