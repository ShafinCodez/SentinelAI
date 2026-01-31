FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for Tree-sitter and Semgrep
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Semgrep CLI
RUN pip install semgrep

COPY . .

# Add current directory to PYTHONPATH
ENV PYTHONPATH=/app

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
