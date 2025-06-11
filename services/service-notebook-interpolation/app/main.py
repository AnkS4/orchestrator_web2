from fastapi import FastAPI, HTTPException, UploadFile, File
import shutil
import os
import uuid
from datetime import datetime
import subprocess

from . import config
import sys

app = FastAPI()

DATA_DIR = "/tmp/data"
NOTEBOOK_PATH = os.path.join(DATA_DIR, "notebook.ipynb")
JUPYTER_URL = "http://localhost:8888"
os.makedirs(DATA_DIR, exist_ok=True)

# Track Jupyter process
jupyter_process = None

def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    config.ServiceConfig.logs.append(f"[{timestamp}] {message}")

def cleanup_input():
    input_path = config.ServiceConfig.input_file
    if input_path and os.path.exists(input_path):
        try:
            os.remove(input_path)
            log(f"Input file {input_path} deleted.")
        except Exception as e:
            log(f"Failed to delete input file: {e}")
    config.ServiceConfig.input_file = None


@app.post("/upload-input-file")
async def upload_input_file(file: UploadFile = File(...)):
    # Sanitize filename to prevent path traversal attacks
    filename = os.path.basename(file.filename)
    temp_path = os.path.join(DATA_DIR, filename)

    # If you want to avoid overwriting files, you can add a UUID if file exists:
    if os.path.exists(temp_path):
        name, ext = os.path.splitext(filename)
        unique_id = uuid.uuid4().hex
        filename = f"{name}_{unique_id}{ext}"
        temp_path = os.path.join(DATA_DIR, filename)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    config.ServiceConfig.input_file = temp_path
    log(f"Input file '{filename}' uploaded successfully.")
    return {"message": f"Input file '{filename}' uploaded successfully."}


@app.post("/start")
def start_service():
    global jupyter_process
    if config.ServiceConfig.is_running:
        raise HTTPException(400, "Service already running.")
    if not config.ServiceConfig.input_file:
        raise HTTPException(400, "Upload input file before starting.")

    unique_id = uuid.uuid4().hex
    output_path = os.path.join(DATA_DIR, f"output_{unique_id}.dat")
    config.ServiceConfig.output_file = output_path

    input_dir = DATA_DIR
    if not os.path.exists(NOTEBOOK_PATH):
        with open(NOTEBOOK_PATH, "w") as f:
            f.write('{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 2}')

    import threading
    jupyter_process = subprocess.Popen([
        sys.executable, "-m", "notebook",
        "--notebook-dir", input_dir,
        "--no-browser",
        "--port=8888",
        "--ip=0.0.0.0",
        "--NotebookApp.base_url=/jupyter/",
        "--ServerApp.token=",
        "--ServerApp.password=",
        "--ServerApp.allow_origin='*'",
        "--ServerApp.disable_check_xsrf=True",
        "--allow-root",
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def stream_process_output(stream, log_func):
        for line in iter(stream.readline, ''):
            if line:
                log_func("[JUPYTER] " + line.rstrip())
        stream.close()

    threading.Thread(target=stream_process_output, args=(jupyter_process.stdout, log), daemon=True).start()
    threading.Thread(target=stream_process_output, args=(jupyter_process.stderr, log), daemon=True).start()

    log(f"Jupyter notebook started with PID {jupyter_process.pid}.")
    config.ServiceConfig.is_running = True
    return {"message": "Jupyter notebook running.", "notebook_path": NOTEBOOK_PATH}


@app.get("/status")
def get_status():
    global jupyter_process
    # Check if the Jupyter process is running
    running = jupyter_process is not None and jupyter_process.poll() is None
    status = "running" if running else "stopped"
    config.ServiceConfig.is_running = running
    return {
        "status": status
    }

@app.get("/log")
def get_logs():
    return {"logs": config.ServiceConfig.logs}

@app.post("/stop")
def stop_service():
    global jupyter_process
    if jupyter_process and jupyter_process.poll() is None:
        jupyter_process.terminate()
        log("Jupyter notebook process terminated.")
        jupyter_process = None
        config.ServiceConfig.is_running = False
        return {"message": "Stopping Jupyter notebook.", "status": "stopped"}
    else:
        config.ServiceConfig.is_running = False
        return {"message": "Service is not running.", "status": "stopped"}
