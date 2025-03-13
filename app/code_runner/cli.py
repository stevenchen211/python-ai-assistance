"""
Command Line Interface Module

Provides command line interface to run Python scripts
"""
import os
import sys
import argparse
import logging
from typing import Dict, List, Any
from .script_runner import ScriptRunner
from .api import start_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Python Code Runner')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Run script command
    run_parser = subparsers.add_parser('run', help='Run Python script')
    run_parser.add_argument('file', help='Python script file path')
    run_parser.add_argument('--venv', help='Virtual environment path')
    
    # Start API service command
    api_parser = subparsers.add_parser('api', help='Start API service')
    api_parser.add_argument('--host', default='0.0.0.0', help='Host address')
    api_parser.add_argument('--port', type=int, default=5000, help='Port number')
    api_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    api_parser.add_argument('--venv', help='Virtual environment path')
    api_parser.add_argument('--static', help='Static files directory path')
    
    return parser.parse_args()


def run_script(file_path: str, venv_path: str = None):
    """
    Run Python script
    
    Args:
        file_path: Script file path
        venv_path: Virtual environment path
    """
    # Check if file exists
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        sys.exit(1)
    
    # Read script content
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Create script runner
    script_runner = ScriptRunner(venv_path=venv_path)
    
    # Log callback function
    def log_callback(message):
        logger.info(message)
    
    # Run script
    script_id = script_runner.run_script(code, log_callback)
    
    # Continuously get logs
    while True:
        logs = script_runner.get_logs(script_id)
        
        # Check if script has finished
        status = script_runner.get_script_status(script_id)
        if status['status'] == 'finished':
            break
        
        # Wait for a while
        import time
        time.sleep(0.5)


def main():
    """Main function"""
    args = parse_args()
    
    if args.command == 'run':
        run_script(args.file, args.venv)
    elif args.command == 'api':
        logger.info(f"Starting FastAPI service, address: {args.host}:{args.port}")
        start_api(host=args.host, port=args.port, debug=args.debug, static_dir=args.static)
    else:
        logger.error("No command specified, please use 'run' or 'api' command")
        sys.exit(1)


if __name__ == '__main__':
    main() 