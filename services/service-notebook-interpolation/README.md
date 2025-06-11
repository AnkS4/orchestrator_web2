# Dockerized Jupyter Notebook Service API

This API allows you to upload files, manage a Jupyter Notebook server, and retrieve logs and status.

---

## Endpoints

### `POST /upload-input-file`

**Upload an input file to the service's data directory.**
---

### `POST /start`

**Start the Jupyter Notebook server (if not already running).**
---

### `POST /stop`

**Stop the Jupyter Notebook server (if running).**
---

### `GET /status`

**Check the status of the Jupyter Notebook server.**
---

### `GET /log`

**Retrieve the service logs, including Jupyter output.**
---

## Service Lifecycle

1. **Upload Input File:**
   Call `/upload-input-file` to upload the data to be processed.
2. **Start Notebook:**
   Call `/start` to initialize and run the Jupyter Notebook server.
3. **Check Status:**
   Use `/status` to see if the notebook is running.
4. **Get Logs:**
   Use `/log` to retrieve logs (including Jupyter output).
5. **Stop Notebook:**
   Call `/stop` to terminate the notebook server.

---


## Usage

1. docker build -t service-notebook:latest .
2. docker run -p 8000:80 service-notebook
3. Follow the service lifecycle steps explained previously!
4. Remember: the notebook will be available in the /jupyter/ endpoint