"""
Test Runner Script

Used to test the ScriptRunner directly
"""
import time
import sys
import os

# 添加父目录到sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.code_runner.script_runner import ScriptRunner

def log_callback(message):
    """Log callback function"""
    print(f"LOG: {message}")

def main():
    """Main function"""
    print("Starting test runner")
    
    # Create script runner
    script_runner = ScriptRunner()
    
    # Test script content
    test_script = """
import time
import sys

print("Test script started")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

# 打印一些信息
for i in range(5):
    print(f"Step {i+1}/5 processing...")
    time.sleep(0.5)
    print(f"Step {i+1} completed")

print("Test script completed")
"""
    
    # Run script
    print("Running test script")
    script_id = script_runner.run_script(test_script, log_callback)
    
    # Get logs periodically
    print(f"Script ID: {script_id}")
    
    # Wait for script to complete
    max_wait = 30  # 最多等待30秒
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