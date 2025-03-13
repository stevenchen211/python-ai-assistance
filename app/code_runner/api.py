"""
API Interface Module

Provides HTTP API interface to run Python scripts and get real-time logs
"""
import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify, Response, stream_with_context
from .script_runner import ScriptRunner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)

# Create script runner
script_runner = ScriptRunner()

# Dictionary to store logs
script_logs = {}


@app.route('/api/run', methods=['POST'])
def run_script():
    """
    Run Python Script API
    
    Request body:
    {
        "code": "Python code"
    }
    
    Response:
    {
        "script_id": "Script ID",
        "message": "Script has started running"
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({
                'error': 'Missing code parameter'
            }), 400
        
        code = data['code']
        
        # Initialize log list
        script_id = None
        
        def log_callback(message):
            nonlocal script_id
            if script_id:
                if script_id not in script_logs:
                    script_logs[script_id] = []
                script_logs[script_id].append(message)
        
        # Run script
        script_id = script_runner.run_script(code, log_callback)
        
        # Initialize logs
        if script_id not in script_logs:
            script_logs[script_id] = []
        
        return jsonify({
            'script_id': script_id,
            'message': 'Script has started running'
        })
        
    except Exception as e:
        logger.error(f"Error in run script API: {str(e)}")
        return jsonify({
            'error': f'Error running script: {str(e)}'
        }), 500


@app.route('/api/logs/<script_id>', methods=['GET'])
def get_logs(script_id):
    """
    Get Script Logs API
    
    Response:
    {
        "logs": ["Log 1", "Log 2", ...]
    }
    """
    try:
        # Get new logs
        new_logs = script_runner.get_logs(script_id)
        
        # Add to log storage
        if script_id not in script_logs:
            script_logs[script_id] = []
        
        script_logs[script_id].extend(new_logs)
        
        return jsonify({
            'logs': script_logs[script_id]
        })
        
    except Exception as e:
        logger.error(f"Error in get logs API: {str(e)}")
        return jsonify({
            'error': f'Error getting logs: {str(e)}'
        }), 500


@app.route('/api/stream-logs/<script_id>', methods=['GET'])
def stream_logs(script_id):
    """
    Stream Script Logs API
    
    Response: Event stream
    """
    def generate():
        # Initialize log index
        if script_id not in script_logs:
            script_logs[script_id] = []
        
        log_index = 0
        
        while True:
            # Get new logs
            new_logs = script_runner.get_logs(script_id)
            
            # Add to log storage
            script_logs[script_id].extend(new_logs)
            
            # Send new logs
            current_logs = script_logs[script_id]
            while log_index < len(current_logs):
                log = current_logs[log_index]
                log_index += 1
                yield f"data: {json.dumps({'log': log})}\n\n"
            
            # Check if script has ended
            status = script_runner.get_script_status(script_id)
            if status['status'] == 'finished':
                yield f"data: {json.dumps({'log': f'Script has ended, return code: {status.get('return_code')}', 'finished': True})}\n\n"
                break
            
            # Wait for a while
            time.sleep(0.5)
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream'
    )


@app.route('/api/status/<script_id>', methods=['GET'])
def get_status(script_id):
    """
    Get Script Status API
    
    Response:
    {
        "script_id": "Script ID",
        "status": "running|finished|not_found",
        ...
    }
    """
    try:
        status = script_runner.get_script_status(script_id)
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error in get status API: {str(e)}")
        return jsonify({
            'error': f'Error getting status: {str(e)}'
        }), 500


@app.route('/api/stop/<script_id>', methods=['POST'])
def stop_script(script_id):
    """
    Stop Script API
    
    Response:
    {
        "script_id": "Script ID",
        "message": "Script has been stopped"
    }
    """
    try:
        success = script_runner.stop_script(script_id)
        
        if success:
            return jsonify({
                'script_id': script_id,
                'message': 'Script has been stopped'
            })
        else:
            return jsonify({
                'script_id': script_id,
                'message': 'Script does not exist or has already ended'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in stop script API: {str(e)}")
        return jsonify({
            'error': f'Error stopping script: {str(e)}'
        }), 500


def start_api(host='0.0.0.0', port=5000, debug=False):
    """
    Start API service
    
    Args:
        host: Host address
        port: Port number
        debug: Whether to enable debug mode
    """
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    start_api(debug=True)