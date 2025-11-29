FROM python:3.11-slim

#prevent Python from buffering outputs and creating .pyc files
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

#install packages playwright needs
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

#install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#install playwright browser
RUN playwright install --with-deps chromium

#copy the entire project into the container
COPY . .

#flask environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_PORT=5000
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000

#start flask app
CMD ["flask", "run"]
