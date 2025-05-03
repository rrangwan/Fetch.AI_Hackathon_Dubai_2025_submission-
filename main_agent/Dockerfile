# Use the official Python image as a base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

ENV PORT 8000
ENV SEED 42
ENV ASI1_API_KEY "key"
ENV WAVER_ADDRESS "localhost:8000"

# Create a .env file with environment variables
RUN echo "PORT=$PORT" > .env && \
    echo "SEED=$SEED" >> .env && \
    echo "ASI1_API_KEY=$ASI1_API_KEY" >> .env && \
    echo "WAVER_ADDRESS=$WAVER_ADDRESS" >> .env

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy the project files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --no-interaction --no-ansi

COPY dev_run.sh ./
RUN chmod +x dev_run.sh

# Copy the rest of the application code
COPY . .

# Set the entrypoint
CMD ["./dev_run.sh"]