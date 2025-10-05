FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    python3-dev \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt gunicorn mysqlclient

# Copy project code
COPY . .

# Set working directory where manage.py is
WORKDIR /app/backend

# Collect static files (run AFTER copying the full project)
RUN python manage.py collectstatic --noinput

# Run Gunicorn from the correct root
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
