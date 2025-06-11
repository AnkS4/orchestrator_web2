from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
import shutil
import os
import uuid
from datetime import datetime

from . import config
import importlib.util
import sys

app = FastAPI()

spec = importlib.util.spec_from_file_location("service", "service.py")
service = importlib.util.module_from_spec(spec)
sys.modules["service"] = service
spec.loader.exec_module(service)

DATA_DIR = "/tmp/data"
os.makedirs(DATA_DIR, exist_ok=True)

def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    config.ServiceConfig.logs.append(f"[{timestamp}] {message}")

def log_progress(percent: int):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    config.ServiceConfig.progress = percent
    config.ServiceConfig.progress_logs.append(f"[{timestamp}] {percent}% completed")

def cleanup_input():
    input_path = config.ServiceConfig.input_file
    if input_path and os.path.exists(input_path):
        try:
            os.remove(input_path)
            log(f"Input file {input_path} deleted.")
        except Exception as e:
            log(f"Failed to delete input file: {e}")
    config.ServiceConfig.input_file = None

def background_task(output_filename):
    log("Background task starting.")
    try:
        service.run_service(
            config.ServiceConfig.input_file,
            config.ServiceConfig.output_file,
            log,
            log_progress,
        )
        config.ServiceConfig.is_running = False
        cleanup_input()
    except Exception as e:
        log(f"Service failed: {e}")
        config.ServiceConfig.is_running = False
        cleanup_input()

@app.post("/upload-input-file")
async def upload_input_file(file: UploadFile = File(...)):
    file_ext = os.path.splitext(file.filename)[-1]
    unique_id = uuid.uuid4().hex
    temp_path = os.path.join(DATA_DIR, f"input_{unique_id}{file_ext}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    config.ServiceConfig.input_file = temp_path
    log("Input file uploaded successfully.")
    return {"message": "Input file uploaded successfully."}

@app.post("/start")
def start_service(bg: BackgroundTasks):
    if config.ServiceConfig.is_running:
        raise HTTPException(400, "Service already running.")
    if not config.ServiceConfig.input_file:
        raise HTTPException(400, "Upload input file before starting.")

    # Assign unique output file name
    unique_id = uuid.uuid4().hex
    output_path = os.path.join(DATA_DIR, f"output_{unique_id}.dat")
    config.ServiceConfig.output_file = output_path

    config.ServiceConfig.is_running = True
    config.ServiceConfig.progress = 0
    config.ServiceConfig.logs = []
    config.ServiceConfig.progress_logs = []

    bg.add_task(background_task, output_path)
    return {"message": "Service started."}

@app.get("/status")
def get_status():
    return {
        "progress": config.ServiceConfig.progress,
        "progress_logs": config.ServiceConfig.progress_logs,
        "is_running": config.ServiceConfig.is_running,
    }

@app.get("/log")
def get_logs():
    return {"logs": config.ServiceConfig.logs}

@app.post("/stop")
def stop_service():
    if config.ServiceConfig.is_running:
        config.ServiceConfig.is_running = False
        log("Service stop requested.")
        return {"message": "Stopping service."}
    else:
        return {"message": "Service is not running."}

@app.get("/download-output-file")
def download_output_file():
    path = config.ServiceConfig.output_file
    if not path or not os.path.exists(path):
        raise HTTPException(404, "No output file available yet.")
    filename = os.path.basename(path)
    # Schedule file for deletion after sending
    response = FileResponse(
        path,
        filename=filename,
        media_type="application/octet-stream",
        background=BackgroundTasks().add_task(os.remove, path),
    )
    # Also reset the output file reference for next run
    config.ServiceConfig.output_file = None
    return response
