FROM python:3.9-slim

WORKDIR /app

# Install necessary system packages
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Ensure the app directory exists and copy its content
COPY . /app

ENV FLASK_APP=app.app

# Run the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]
