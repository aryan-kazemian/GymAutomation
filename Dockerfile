# Use official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies including libpq-dev for psycopg2 and ODBC support
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    gcc \
    postgresql-client \
    libpq-dev \
    unixodbc \
    unixodbc-dev \
    libodbc1 \
    libodbc2 \
    odbcinst \
    odbcinst1debian2 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . /app/

# Add entrypoint script and make it executable
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command to run Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
