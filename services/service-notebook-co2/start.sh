#!/bin/bash
# Start FastAPI app
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
# Start nginx (foreground)
nginx -g "daemon off;"
