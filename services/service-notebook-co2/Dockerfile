FROM python:3.10-slim

# Install nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install fastapi uvicorn pydantic python-multipart httpx notebook

COPY app ./app
COPY nginx.conf /etc/nginx/nginx.conf
COPY notebook.ipynb /tmp/data/notebook.ipynb

COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]