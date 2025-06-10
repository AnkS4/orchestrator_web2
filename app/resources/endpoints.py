from flask_restful import Resource
from flask import request, send_file, current_app, redirect
import os
import requests
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from pathlib import Path

service_runs = []
DATA_DIR = "/static/files/"


def get_logger():
    """Get the application logger"""
    return current_app.config['APP_LOGGER']


class UploadFile(Resource):
    def post(self):
        # Get service name from URL parameter
        service_name = request.args.get('service', 'co2')  # Default to co2

        logger = get_logger()

        try:
            if 'file' not in request.files:
                logger.error('No file part in the request')
                return {'message': 'No file part in the request'}, 400

            file = request.files['file']
            if not file.filename:
                logger.error('No file selected for uploading')
                return {'message': 'No file selected for uploading'}, 400

            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            port = 0

            if service_name == 'co2':
                port = 8001
            elif service_name == 'interpolation':
                port = 8002
            elif service_name == 'agrixels':
                port = 8003
            else:
                port = 8001

            # Upload file
            url_upload = f"http://localhost:{port}/upload-input-file"

            try:
                with open(filepath, 'rb') as f:
                    files = {'file': (filepath, f, 'text/csv')}
                    headers = {
                        'Accept': 'application/json'
                    }
                    response_upload = requests.post(url_upload, headers=headers, files=files)
                    response_upload.raise_for_status()
            except Exception as e:
                logger.error(f'Failed to upload input file: {str(e)}')
                return {'message': 'Failed to upload input file'}, 500

            logger.info(f'File uploaded successfully: {filename}')
            return {'message': f'File {filename} uploaded successfully'}, 201

        except Exception as e:
            logger.error(f'Upload error: {str(e)}')
            return {'message': 'Upload failed'}, 500


class StartService(Resource):
    def post(self):
        global service_runs
        logger = get_logger()

        # Get service name from URL parameter
        service_name = request.args.get('service', 'co2')  # Default to co2
        service_uuid = str(uuid.uuid4())
        start_time = datetime.now().isoformat()

        result_filename = f'result_{service_uuid}.csv'

        result_path = os.path.abspath(os.path.join(current_app.config['RESULT_FOLDER'], result_filename))

        try:
            with open(result_path, 'w') as f:
                pass
        except Exception as e:
            logger.error(f'Failed to create result file: {str(e)}')
            return {'message': 'Failed to create result file'}, 500

        # SERVICE-SPECIFIC CONFIGURATION
        result_path = ""
        port = 0

        if service_name == 'co2':
            logger.info(f'Service 1 execution started with UUID: {service_uuid}')
            port = 8001
        elif service_name == 'interpolation':
            logger.info(f'Service 2 execution started with UUID: {service_uuid}')
            port = 8002
        elif service_name == 'agrixels':
            logger.info(f'Service 3 execution started with UUID: {service_uuid}')
            # Set result file for agrixels
            result_path = os.path.join(DATA_DIR, "result.csv")
        else:
            # Default to Service 1
            logger.info(f'Service 1 execution started with UUID: {service_uuid}')
            port = 8001

        service_run = {
            'uuid': service_uuid,
            'start_time': start_time,
            'status': 'running',
            'result_file': result_path,
            'end_time': None,
            'service_name': service_name,
            'port': port
        }
        service_runs.append(service_run)

        # For services 1 and 2, trigger notebook server
        if service_name in ['co2', 'interpolation']:
            try:
                # Start notebook server
                url = f"http://localhost:{port}/start"
                headers = {'Accept': 'application/json'}
                response = requests.post(url, headers=headers)
                response.raise_for_status()

                return {
                    "message": "Service started successfully",
                    "service_uuid": service_uuid,
                    "notebook_url": f"http://{request.host.split(':')[0]}:{port}/jupyter"
                }
            except Exception as e:
                logger.error(f'Failed to start notebook server: {str(e)}')
                return {'message': 'El archivo no se ha cargado o el servicio ya está en funcionamiento!'}, 500

        elif service_name == 'agrixels':
            return {
                "message": "Archivo Agrixels generado!",
                "service_uuid": service_uuid,
                "static_file": result_path
            }


class OpenNotebook(Resource):
    def get(self):
        service_uuid = request.args.get('uuid')
        target_run = next((run for run in service_runs if run['uuid'] == service_uuid), None)

        if not target_run:
            return {"message": "Service not found"}, 404

        port = target_run.get('port')
        service_name = target_run.get('service_name')
        if not port:
            return {"message": "Port not configured for this service"}, 404

        # Build the subdomain URL for the service
        redirect_url = f"http://{service_name}.{request.host}/jupyter"
        return redirect(redirect_url, code=302)


class CheckStatus(Resource):
    def get(self):
        global service_runs
        logger = get_logger()

        running_count = len([run for run in service_runs if run['status'] == 'running'])
        response_data = {
            'timestamp': datetime.now().isoformat(),
            'total_services': len(service_runs),
            'running_services': running_count,
            'service_runs': []
        }
        for run in reversed(service_runs):
            service_info = {
                'service_uuid': run['uuid'],
                'status': run['status'],
                'start_time': run['start_time'],
                'result_available': os.path.exists(run['result_file']) if run['result_file'] else False,
                'service_name': run['service_name']
            }
            if run['end_time']:
                service_info['end_time'] = run['end_time']
            response_data['service_runs'].append(service_info)

        logger.info(f'Status check: {len(service_runs)} total services, {running_count} running')
        return response_data


class DownloadResult(Resource):
    def get(self):
        logger = get_logger()

        result_file = os.path.join(os.path.dirname(current_app.root_path), "static/files/result.csv")

        if not Path(result_file).exists():
            logger.error(f'Download attempted but result file does not exist on disk: {result_file}')
            return {'message': 'Archivo de resultados no encontrado en el disco.'}, 404

        try:
            logger.info(f'Result file downloaded!')
            return send_file(result_file, as_attachment=True, download_name=os.path.basename(result_file))

        except Exception as e:
            logger.error(f'Error sending file: {str(e)}')
            return {'message': 'Error al descargar el archivo.'}, 500


class LogService(Resource):
    def get(self):
        logger = get_logger()
        try:
            log_file = current_app.config['LOG_FILE']
            if not os.path.exists(log_file):
                return {'message': 'Log file not found'}, 404

            with open(log_file, 'r') as f:
                logs = f.read()

            logger.info('Logs retrieved')
            return {'logs': logs}

        except Exception as e:
            logger.error(f'Log retrieval error: {str(e)}')
            return {'message': 'Failed to retrieve logs'}, 500


def register_resources(api):
    api.add_resource(UploadFile, '/api/upload')
    api.add_resource(StartService, '/api/start')
    api.add_resource(CheckStatus, '/api/status')
    api.add_resource(DownloadResult, '/api/download')
    api.add_resource(LogService, '/api/logs')
    api.add_resource(OpenNotebook, '/api/open-notebook')
