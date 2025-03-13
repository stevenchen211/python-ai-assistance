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