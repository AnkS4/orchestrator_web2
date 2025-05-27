from flask_restful import Resource
from flask import request, send_file, current_app
import os
import threading
import time
import logging
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

# Service status tracker with UUID support
service_status = {'running': False, 'result_file': None, 'service_uuid': None, 'start_time': None}


class UploadFile(Resource):
    def post(self):
        try:
            if 'file' not in request.files:
                logging.error('No file part in the request')
                return {'message': 'No file part in the request'}, 400

            file = request.files['file']
            if not file.filename:
                logging.error('No file selected for uploading')
                return {'message': 'No file selected for uploading'}, 400

            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            logging.info(f'File uploaded successfully: {filename}')
            return {'message': f'File {filename} uploaded successfully'}, 201

        except Exception as e:
            logging.error(f'Upload error: {str(e)}')
            return {'message': 'Upload failed'}, 500


class StartService(Resource):
    def post(self):
        global service_status

        if service_status['running']:
            logging.warning('Service start attempted while already running')
            return {'message': 'Service already running'}, 409

        # Generate unique UUID for this service execution
        service_uuid = str(uuid.uuid4())
        service_status['service_uuid'] = service_uuid
        service_status['start_time'] = datetime.now().isoformat()

        def run_service():
            try:
                service_status['running'] = True
                logging.info(f'Service execution started with UUID: {service_uuid}')

                # Simulate service work
                time.sleep(3)

                # Create result file with UUID in filename
                result_filename = f'result_{service_uuid}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
                result_path = os.path.join(current_app.config['RESULT_FOLDER'], result_filename)

                with open(result_path, 'w') as f:
                    f.write(f'Service execution completed at {datetime.now()}\n')
                    f.write(f'Service UUID: {service_uuid}\n')
                    f.write('Sample processing results:\n')
                    f.write('- Data processed successfully\n')
                    f.write('- 100 records analyzed\n')
                    f.write(f'- Execution started at: {service_status["start_time"]}\n')

                service_status['result_file'] = result_path
                logging.info(f'Service execution completed. UUID: {service_uuid}, Result saved to {result_path}')

            except Exception as e:
                logging.error(f'Service execution error for UUID {service_uuid}: {str(e)}')
            finally:
                service_status['running'] = False

        thread = threading.Thread(target=run_service)
        thread.start()

        logging.info(f'Service start request accepted with UUID: {service_uuid}')
        return {
            'message': 'Service started successfully',
            'service_uuid': service_uuid,
            'start_time': service_status['start_time']
        }, 202


class CheckStatus(Resource):
    def get(self):
        global service_status

        status = 'running' if service_status['running'] else 'stopped'
        result_available = service_status['result_file'] is not None

        response_data = {
            'status': status,
            'result_available': result_available,
            'timestamp': datetime.now().isoformat()
        }

        # Include service UUID and start time if available
        if service_status['service_uuid']:
            response_data['service_uuid'] = service_status['service_uuid']
            response_data['start_time'] = service_status['start_time']

        logging.info(
            f'Status check: {status}, UUID: {service_status.get("service_uuid", "None")}, result available: {result_available}')

        return response_data


class DownloadResult(Resource):
    def get(self):
        global service_status

        if not service_status['result_file'] or not os.path.exists(service_status['result_file']):
            logging.error('Download attempted but result file not found')
            return {'message': 'Result file not available'}, 404

        logging.info(f'Result file downloaded for UUID: {service_status.get("service_uuid", "Unknown")}')
        return send_file(service_status['result_file'], as_attachment=True)


class LogService(Resource):
    def get(self):
        try:
            log_file = current_app.config['LOG_FILE']
            if not os.path.exists(log_file):
                return {'message': 'Log file not found'}, 404

            with open(log_file, 'r') as f:
                logs = f.read()

            logging.info('Logs retrieved')
            return {'logs': logs}

        except Exception as e:
            logging.error(f'Log retrieval error: {str(e)}')
            return {'message': 'Failed to retrieve logs'}, 500


def register_resources(api):
    api.add_resource(UploadFile, '/api/upload')
    api.add_resource(StartService, '/api/start')
    api.add_resource(CheckStatus, '/api/status')
    api.add_resource(DownloadResult, '/api/download')
    api.add_resource(LogService, '/api/logs')
