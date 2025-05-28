from flask_restful import Resource
from flask import request, send_file, current_app
import os
import threading
import time
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

service_runs = []


def get_logger():
    """Get the application logger"""
    return current_app.config['APP_LOGGER']


class UploadFile(Resource):
    def post(self):
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

            logger.info(f'File uploaded successfully: {filename}')
            return {'message': f'File {filename} uploaded successfully'}, 201

        except Exception as e:
            logger.error(f'Upload error: {str(e)}')
            return {'message': 'Upload failed'}, 500


class StartService(Resource):
    def post(self):
        global service_runs
        logger = get_logger()

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

        service_run = {
            'uuid': service_uuid,
            'start_time': start_time,
            'status': 'running',
            'result_file': result_path,
            'result_filename': result_filename,
            'end_time': None
        }
        service_runs.append(service_run)

        def run_service():
            try:
                logger.info(f'Service execution started with UUID: {service_uuid}')
                time.sleep(3)

                with open(result_path, 'w') as f:
                    f.write('timestamp,service_uuid,status\n')
                    f.write(f'{datetime.now().isoformat()},{service_uuid},completed\n')

                for run in service_runs:
                    if run['uuid'] == service_uuid:
                        run['status'] = 'completed'
                        run['end_time'] = datetime.now().isoformat()
                        break

                logger.info(f'Service execution completed. UUID: {service_uuid}, Result saved to {result_path}')

            except Exception as e:
                logger.error(f'Service execution error for UUID {service_uuid}: {str(e)}')
                for run in service_runs:
                    if run['uuid'] == service_uuid:
                        run['status'] = 'error'
                        run['end_time'] = datetime.now().isoformat()
                        break

        thread = threading.Thread(target=run_service)
        thread.start()

        logger.info(f'Service start request accepted with UUID: {service_uuid}')
        return {
            'message': 'Service started successfully',
            'service_uuid': service_uuid,
            'start_time': start_time,
            'result_filename': result_filename
        }, 202


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
                'result_available': run['result_filename'] if run['result_file'] else None
            }
            if run['end_time']:
                service_info['end_time'] = run['end_time']
            response_data['service_runs'].append(service_info)

        logger.info(f'Status check: {len(service_runs)} total services, {running_count} running')
        return response_data


class DownloadResult(Resource):
    def get(self):
        global service_runs
        logger = get_logger()

        service_uuid = request.args.get('uuid')

        if service_uuid:
            target_run = next((run for run in service_runs if run['uuid'] == service_uuid), None)
            if not target_run or not target_run['result_file']:
                logger.error(f'Download attempted for UUID {service_uuid} but result file not found')
                return {'message': f'Result file not available for UUID {service_uuid}'}, 404
            result_file = target_run['result_file']
        else:
            completed_runs = [run for run in service_runs if run['result_file']]
            if not completed_runs:
                logger.error('Download attempted but no result files available')
                return {'message': 'No result files available'}, 404
            target_run = max(completed_runs, key=lambda x: x['start_time'])
            result_file = target_run['result_file']

        if not os.path.exists(result_file):
            logger.error(f'Download attempted but result file does not exist on disk: {result_file}')
            return {'message': 'Result file not found on disk'}, 404

        try:
            logger.info(f'Result file downloaded for UUID: {target_run["uuid"]}')
            return send_file(result_file, as_attachment=True, download_name=target_run['result_filename'])
        except Exception as e:
            logger.error(f'Error sending file: {str(e)}')
            return {'message': 'Error downloading file'}, 500


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
