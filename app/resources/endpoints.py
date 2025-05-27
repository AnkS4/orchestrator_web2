from flask_restful import Resource
from flask import request, send_file, current_app
import os
import threading
import time
import logging
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

service_runs = []

class UploadFile(Resource):
    # ... (unchanged)
    pass

class StartService(Resource):
    def post(self):
        global service_runs

        running_services = [run for run in service_runs if run['status'] == 'running']
        if running_services:
            logging.warning('Service start attempted while another service is running')
            return {'message': 'Another service is already running'}, 409

        service_uuid = str(uuid.uuid4())
        start_time = datetime.now().isoformat()
        result_filename = f'result_{service_uuid}.csv'
        result_path = os.path.join(current_app.config['RESULT_FOLDER'], result_filename)

        # Create empty CSV file immediately
        with open(result_path, 'w') as f:
            pass

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
                logging.info(f'Service execution started with UUID: {service_uuid}')
                # Simulate service work
                time.sleep(3)
                # (You can write more to the CSV here if needed)
                for run in service_runs:
                    if run['uuid'] == service_uuid:
                        run['status'] = 'completed'
                        run['end_time'] = datetime.now().isoformat()
                        break
                logging.info(f'Service execution completed. UUID: {service_uuid}, Result saved to {result_path}')
            except Exception as e:
                logging.error(f'Service execution error for UUID {service_uuid}: {str(e)}')
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
            'start_time': start_time,
            'result_filename': result_filename
        }, 202

class CheckStatus(Resource):
    def get(self):
        global service_runs
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
        logging.info(f'Status check: {len(service_runs)} total services, {running_count} running')
        return response_data

class DownloadResult(Resource):
    def get(self):
        global service_runs
        service_uuid = request.args.get('uuid')
        if service_uuid:
            target_run = next((run for run in service_runs if run['uuid'] == service_uuid), None)
            if not target_run or not target_run['result_file']:
                logging.error(f'Download attempted for UUID {service_uuid} but result file not found')
                return {'message': f'Result file not available for UUID {service_uuid}'}, 404
            result_file = target_run['result_file']
        else:
            completed_runs = [run for run in service_runs if run['result_file']]
            if not completed_runs:
                logging.error('Download attempted but no result files available')
                return {'message': 'No result files available'}, 404
            target_run = max(completed_runs, key=lambda x: x['start_time'])
            result_file = target_run['result_file']
        if not os.path.exists(result_file):
            logging.error('Download attempted but result file does not exist on disk')
            return {'message': 'Result file not found on disk'}, 404
        logging.info(f'Result file downloaded for UUID: {target_run["uuid"]}')
        return send_file(result_file, as_attachment=True)

class LogService(Resource):
    # ... (unchanged)
    pass

def register_resources(api):
    api.add_resource(UploadFile, '/api/upload')
    api.add_resource(StartService, '/api/start')
    api.add_resource(CheckStatus, '/api/status')
    api.add_resource(DownloadResult, '/api/download')
    api.add_resource(LogService, '/api/logs')
