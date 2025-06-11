# Dockerized Service

## Endpoints

- `POST /path-to-file`      { "path": "path/to/input" }
- `POST /path-to-output-file` { "path": "path/to/output" }
- `POST /start`             Starts the service (requires both paths set)
- `POST /stop`              Stops the service
- `GET /status`             Gets service progress
- `GET /log`                Retrieves service logs

## Usage

1. Implement your service in `service.py`
2. Build image: `docker build -t myservice .`
3. Run: `docker run -p 8000:8000 myservice`
4. Interact via API (e.g., Postman or `curl`).
