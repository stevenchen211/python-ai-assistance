"""
Script Runner Module

Used to run Python scripts and get real-time logs
"""
import os
import sys
import uuid
import time
import signal
import tempfile
import threading
import subprocess
import logging
from typing import Dict, List, Any, Optional, Callable, Tuple
from queue import Queue, Empty
from .dependency_manager import DependencyManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScriptRunner:
    """Python Script Runner"""
    
    def __init__(self, venv_path: Optional[str] = None, scripts_dir: Optional[str] = None):
        """
        Initialize script runner
        
        Args:
            venv_path: Virtual environment path, if None, use system Python environment
            scripts_dir: Script storage directory, if None, use temporary directory
        """
        self.venv_path = venv_path
        self.scripts_dir = scripts_dir or tempfile.gettempdir()
        self.dependency_manager = DependencyManager(venv_path)
        self.running_scripts = {}  # Running scripts {script_id: process_info}
        
        # Create script directory
        os.makedirs(self.scripts_dir, exist_ok=True)
    
    def _generate_script_id(self) -> str:
        """
        Generate script ID
        
        Returns:
            Script ID
        """
        return str(uuid.uuid4())
    
    def _save_script(self, code: str) -> Tuple[str, str]:
        """
        Save script to file
        
        Args:
            code: Python code
            
        Returns:
            Tuple of script ID and script file path
        """
        script_id = self._generate_script_id()
        script_path = os.path.join(self.scripts_dir, f"{script_id}.py")
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        return script_id, script_path
    
    def _read_output(self, process, output_queue: Queue, script_id: str):
        """
        Read process output and put into queue
        
        Args:
            process: Child process
            output_queue: Output queue
            script_id: Script ID
        """
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            output_queue.put((script_id, line.strip()))
        
        process.stdout.close()
    
    def _read_error(self, process, output_queue: Queue, script_id: str):
        """
        Read process error output and put into queue
        
        Args:
            process: Child process
            output_queue: Output queue
            script_id: Script ID
        """
        for line in iter(process.stderr.readline, ''):
            if not line:
                break
            output_queue.put((script_id, f"ERROR: {line.strip()}"))
        
        process.stderr.close()
    
    def run_script(self, code: str, log_callback: Optional[Callable[[str], None]] = None) -> str:
        """
        Run Python script
        
        Args:
            code: Python code
            log_callback: Log callback function
            
        Returns:
            Script ID
        """
        # Save script to file
        script_id, script_path = self._save_script(code)
        
        if log_callback:
            log_callback(f"Script ID: {script_id}")
            log_callback(f"Script saved to: {script_path}")
        
        # Prepare script environment
        if not self.dependency_manager.prepare_script(code, log_callback):
            if log_callback:
                log_callback("Failed to prepare script environment, cannot run script")
            return script_id
        
        # Get Python executable path
        python_executable = self.dependency_manager.python_executable
        
        # Create output queue
        output_queue = Queue()
        
        try:
            # Start process
            process = subprocess.Popen(
                [python_executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            if log_callback:
                log_callback(f"Script started running, process ID: {process.pid}")
            
            # Create threads to read output
            stdout_thread = threading.Thread(
                target=self._read_output,
                args=(process, output_queue, script_id)
            )
            stderr_thread = threading.Thread(
                target=self._read_error,
                args=(process, output_queue, script_id)
            )
            
            # Set as daemon threads
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            
            # Start threads
            stdout_thread.start()
            stderr_thread.start()
            
            # Save process information
            self.running_scripts[script_id] = {
                'process': process,
                'output_queue': output_queue,
                'stdout_thread': stdout_thread,
                'stderr_thread': stderr_thread,
                'start_time': time.time()
            }
            
            return script_id
            
        except Exception as e:
            error_msg = f"Error running script: {str(e)}"
            if log_callback:
                log_callback(error_msg)
            logger.error(error_msg)
            return script_id
    
    def get_logs(self, script_id: str, timeout: float = 0.1) -> List[str]:
        """
        Get script logs
        
        Args:
            script_id: Script ID
            timeout: Wait timeout (seconds)
            
        Returns:
            List of logs
        """
        if script_id not in self.running_scripts:
            return [f"Script {script_id} does not exist or has ended"]
        
        script_info = self.running_scripts[script_id]
        output_queue = script_info['output_queue']
        logs = []
        
        try:
            while True:
                try:
                    # Get log from queue
                    _, log = output_queue.get(block=True, timeout=timeout)
                    logs.append(log)
                except Empty:
                    # Queue is empty, check if process has ended
                    if not script_info['process'].poll() is None:
                        # Process has ended
                        return_code = script_info['process'].poll()
                        logs.append(f"Script has ended, return code: {return_code}")
                        
                        # Clean up resources
                        self._cleanup_script(script_id)
                    break
        except Exception as e:
            logs.append(f"Error getting logs: {str(e)}")
        
        return logs
    
    def stop_script(self, script_id: str) -> bool:
        """
        Stop script execution
        
        Args:
            script_id: Script ID
            
        Returns:
            Whether successfully stopped
        """
        if script_id not in self.running_scripts:
            return False
        
        script_info = self.running_scripts[script_id]
        process = script_info['process']
        
        try:
            # Try to terminate process
            if sys.platform == 'win32':
                process.terminate()
            else:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            
            # Wait for process to end
            process.wait(timeout=5)
            
            # Clean up resources
            self._cleanup_script(script_id)
            
            return True
        except Exception as e:
            logger.error(f"Error stopping script: {str(e)}")
            return False
    
    def _cleanup_script(self, script_id: str):
        """
        Clean up script resources
        
        Args:
            script_id: Script ID
        """
        if script_id in self.running_scripts:
            # Remove from running scripts dictionary
            del self.running_scripts[script_id]
            
            # Delete script file
            script_path = os.path.join(self.scripts_dir, f"{script_id}.py")
            try:
                if os.path.exists(script_path):
                    os.remove(script_path)
            except Exception as e:
                logger.error(f"Error deleting script file: {str(e)}")
    
    def get_script_status(self, script_id: str) -> Dict[str, Any]:
        """
        Get script status
        
        Args:
            script_id: Script ID
            
        Returns:
            Script status dictionary
        """
        if script_id not in self.running_scripts:
            return {
                'script_id': script_id,
                'status': 'not_found',
                'message': f"Script {script_id} does not exist or has ended"
            }
        
        script_info = self.running_scripts[script_id]
        process = script_info['process']
        
        # Check if process is running
        if process.poll() is None:
            # Process is running
            return {
                'script_id': script_id,
                'status': 'running',
                'pid': process.pid,
                'start_time': script_info['start_time'],
                'run_time': time.time() - script_info['start_time']
            }
        else:
            # Process has ended
            return {
                'script_id': script_id,
                'status': 'finished',
                'return_code': process.poll(),
                'start_time': script_info['start_time'],
                'end_time': time.time(),
                'run_time': time.time() - script_info['start_time']
            } 