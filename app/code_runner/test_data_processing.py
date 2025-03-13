"""
Test Data Processing Example

Used to test the data processing example
"""
import time
import sys
import os

# 添加父目录到sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.code_runner.script_runner import ScriptRunner
from app.code_runner.test_examples import get_data_processing_example

def log_callback(message):
    """Log callback function"""
    print(f"LOG: {message}")

def main():
    """Main function"""
    print("Starting data processing test")
    
    # Create script runner
    script_runner = ScriptRunner()
    
    # Get data processing example
    test_script = get_data_processing_example()
    
    # Run script
    print("Running data processing example")
    script_id = script_runner.run_script(test_script, log_callback)
    
    # Get logs periodically
    print(f"Script ID: {script_id}")
    
    # Wait for script to complete
    max_wait = 60  # 最多等待60秒
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        # Get logs
        logs = script_runner.get_logs(script_id)
        
        # Print logs
        for log in logs:
            print(f"SCRIPT LOG: {log}")
        
        # Check if script has ended
        status = script_runner.get_script_status(script_id)
        if status['status'] == 'finished':
            print(f"Script has ended, return code: {status.get('return_code')}")
            break
        
        # Wait for a while
        time.sleep(1)
    
    print("Test completed")

if __name__ == "__main__":
    main() 