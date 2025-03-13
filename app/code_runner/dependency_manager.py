"""
Dependency Management Module

Used to parse and install dependencies for Python scripts
"""
import os
import re
import sys
import subprocess
import tempfile
import logging
from typing import List, Set, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DependencyManager:
    """Dependency Manager"""
    
    def __init__(self, venv_path: Optional[str] = None):
        """
        Initialize dependency manager
        
        Args:
            venv_path: Virtual environment path, if None, use system Python environment
        """
        self.venv_path = venv_path
        self.python_executable = self._get_python_executable()
        self.pip_executable = self._get_pip_executable()
        
    def _get_python_executable(self) -> str:
        """
        Get Python executable path
        
        Returns:
            Python executable path
        """
        if self.venv_path:
            if sys.platform == 'win32':
                return os.path.join(self.venv_path, 'Scripts', 'python.exe')
            return os.path.join(self.venv_path, 'bin', 'python')
        return sys.executable
    
    def _get_pip_executable(self) -> str:
        """
        Get pip executable path
        
        Returns:
            pip executable path
        """
        if self.venv_path:
            if sys.platform == 'win32':
                return os.path.join(self.venv_path, 'Scripts', 'pip.exe')
            return os.path.join(self.venv_path, 'bin', 'pip')
        
        # Use Python -m pip
        return f"{self.python_executable} -m pip"
    
    def extract_imports(self, code: str) -> Set[str]:
        """
        Extract imported packages from code
        
        Args:
            code: Python code
            
        Returns:
            Set of imported packages
        """
        # Match import statements
        import_pattern = r'^import\s+([a-zA-Z0-9_]+)(?:\s*,\s*([a-zA-Z0-9_]+))*'
        from_pattern = r'^from\s+([a-zA-Z0-9_]+)(?:\.[a-zA-Z0-9_]+)*\s+import'
        
        packages = set()
        
        for line in code.split('\n'):
            line = line.strip()
            
            # Process import statements
            import_match = re.match(import_pattern, line)
            if import_match:
                for group in import_match.groups():
                    if group:
                        packages.add(group)
            
            # Process from statements
            from_match = re.match(from_pattern, line)
            if from_match and from_match.group(1):
                packages.add(from_match.group(1))
        
        # Filter standard libraries
        std_libs = {
            'os', 'sys', 're', 'math', 'datetime', 'time', 'json', 'csv', 'random',
            'collections', 'itertools', 'functools', 'typing', 'pathlib', 'io',
            'argparse', 'logging', 'unittest', 'tempfile', 'shutil', 'glob',
            'pickle', 'hashlib', 'base64', 'uuid', 'copy', 'string', 'textwrap',
            'calendar', 'contextlib', 'subprocess', 'threading', 'multiprocessing',
            'queue', 'socket', 'email', 'urllib', 'http', 'html', 'xml', 'webbrowser',
            'tkinter', 'asyncio', 'concurrent', 'zipfile', 'tarfile', 'gzip', 'bz2',
            'lzma', 'zlib', 'struct', 'array', 'enum', 'statistics', 'traceback',
            'pdb', 'profile', 'timeit', 'trace', 'warnings', 'weakref', 'platform',
            'gc', 'inspect', 'ast', 'symtable', 'token', 'keyword', 'tokenize',
            'tabnanny', 'pyclbr', 'py_compile', 'compileall', 'dis', 'pickletools'
        }
        
        return {pkg for pkg in packages if pkg not in std_libs}
    
    def install_dependencies(self, packages: Set[str], log_callback=None) -> bool:
        """
        Install dependency packages
        
        Args:
            packages: Set of packages to install
            log_callback: Log callback function
            
        Returns:
            Whether installation was successful
        """
        if not packages:
            if log_callback:
                log_callback("No dependencies detected to install")
            return True
        
        # Build pip install command
        pip_cmd = f"{self.pip_executable} install {' '.join(packages)}"
        
        if log_callback:
            log_callback(f"Installing dependencies: {', '.join(packages)}")
        
        try:
            # Execute pip install
            process = subprocess.Popen(
                pip_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output
            for line in process.stdout:
                if log_callback:
                    log_callback(line.strip())
                else:
                    logger.info(line.strip())
            
            # Wait for process to complete
            return_code = process.wait()
            
            if return_code == 0:
                if log_callback:
                    log_callback("Dependencies installed successfully")
                return True
            else:
                if log_callback:
                    log_callback(f"Dependencies installation failed, return code: {return_code}")
                return False
                
        except Exception as e:
            error_msg = f"Error installing dependencies: {str(e)}"
            if log_callback:
                log_callback(error_msg)
            logger.error(error_msg)
            return False
    
    def prepare_script(self, code: str, log_callback=None) -> bool:
        """
        Prepare script environment, install required dependencies
        
        Args:
            code: Python code
            log_callback: Log callback function
            
        Returns:
            Whether preparation was successful
        """
        # Extract imported packages
        packages = self.extract_imports(code)
        
        if log_callback:
            log_callback(f"Detected dependencies: {', '.join(packages) if packages else 'none'}")
        
        # Install dependencies
        return self.install_dependencies(packages, log_callback) 