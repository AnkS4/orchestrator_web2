from flask_restful import Resource
from flask import request, send_file, current_app
import os
import threading
import time
import logging
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

# Service runs tracker - stores all service executions
service_runs = []


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
        global service_runs

        # Check if any service is currently running
        running_services = [run for run in service_runs if run['status'] == 'running']
        if running_services:
            logging.warning('Service start attempted while another service is running')
            return {'message': 'Another service is already running'}, 409

        # Generate unique UUID for this service execution
        service_uuid = str(uuid.uuid4())
        start_time = datetime.now().isoformat()

        # Create new service run entry
        service_run = {
            'uuid': service_uuid,
            'start_time': start_time,
            'status': 'running',
            'result_file': None,
            'end_time': None
        }
        service_runs.append(service_run)

        def run_service():
            try:
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
                    f.write(f'- Execution started at: {start_time}\n')

                # Update the service run status
                for run in service_runs:
                    if run['uuid'] == service_uuid:
                        run['status'] = 'completed'
                        run['result_file'] = result_path
                        run['end_time'] = datetime.now().isoformat()
                        break

                logging.info(f'Service execution completed. UUID: {service_uuid}, Result saved to {result_path}')

            except Exception as e:
                logging.error(f'Service execution error for UUID {service_uuid}: {str(e)}')
                # Update status to error
                for run in service_runs:
                    if run['uuid'] == service_uuid:
                        run['status'] = 'error'
                        run['end_time'] = datetime.now().isoformat()
                        break

        thread = threading.Thread(target=run_service)
        thread.start()

        logging.info(f'Service start request accepted with UUID: {service_uuid}')
        return {
            'message': 'Service started successfully',
            'service_uuid': service_uuid,
            'start_time': start_time
        }, 202


class CheckStatus(Resource):
    def get(self):
        global service_runs

        # Get current running services count
        running_count = len([run for run in service_runs if run['status'] == 'running'])

        # Prepare response with all service runs
        response_data = {
            'timestamp': datetime.now().isoformat(),
            'total_services': len(service_runs),
            'running_services': running_count,
            'service_runs': []
        }

        # Add all service runs to response (most recent first)
        for run in reversed(service_runs):
            service_info = {
                'service_uuid': run['uuid'],
                'status': run['status'],
                'start_time': run['start_time'],
                'result_available': run['result_file'] is not None
            }
            if run['end_time']:
                service_info['end_time'] = run['end_time']

            response_data['service_runs'].append(service_info)

        logging.info(f'Status check: {len(service_runs)} total services, {running_count} running')

        return response_data


class DownloadResult(Resource):
    def get(self):
        global service_runs

        # Get UUID from query parameter (optional)
        service_uuid = request.args.get('uuid')

        if service_uuid:
            # Find specific service by UUID
            target_run = None
            for run in service_runs:
                if run['uuid'] == service_uuid:
                    target_run = run
                    break

            if not target_run or not target_run['result_file']:
                logging.error(f'Download attempted for UUID {service_uuid} but result file not found')
                return {'message': f'Result file not available for UUID {service_uuid}'}, 404

            result_file = target_run['result_file']
        else:
            # Get the most recent completed service
            completed_runs = [run for run in service_runs if run['result_file'] is not None]
            if not completed_runs:
                logging.error('Download attempted but no result files available')
                return {'message': 'No result files available'}, 404

            # Get most recent completed run
            target_run = max(completed_runs, key=lambda x: x['start_time'])
            result_file = target_run['result_file']

        if not os.path.exists(result_file):
            logging.error('Download attempted but result file does not exist on disk')
            return {'message': 'Result file not found on disk'}, 404

        logging.info(f'Result file downloaded for UUID: {target_run["uuid"]}')
        return send_file(result_file, as_attachment=True)


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
