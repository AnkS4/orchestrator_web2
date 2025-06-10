# Python base image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Change permissions for entrypoint
RUN chmod +x entrypoint.sh

# Run the application
ENTRYPOINT ["sh", "entrypoint.sh"]