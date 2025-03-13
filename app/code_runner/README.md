# Python Code Runner

This package provides an API interface for running Python scripts, can solve dependency issues, and provides real-time logging functionality.

## Features

1. **Run Python Scripts**: Run Python scripts through API interface
2. **Dependency Management**: Automatically parse and install dependencies required by scripts
3. **Real-time Logging**: Provides real-time log streaming to monitor script execution status
4. **Script Management**: Manage running scripts, view status and stop execution

## Installation

Make sure you have the required dependencies installed:

```bash
pip install flask
```

## Usage

### Command Line Usage

Start the API service:

```bash
python -m app.code_runner.cli api --port 5000
```

Run a Python script:

```bash
python -m app.code_runner.cli run script.py
```

### API Interface

#### Run Script

```
POST /api/run
```

Request body:

```json
{
    "code": "print('Hello, World!')"
}
```

Response:

```json
{
    "script_id": "script_id",
    "message": "Script has started running"
}
```

#### Get Logs

```
GET /api/logs/<script_id>
```

Response:

```json
{
    "logs": ["log1", "log2", ...]
}
```

#### Stream Logs

```
GET /api/stream-logs/<script_id>
```

Response: Event stream

#### Get Script Status

```
GET /api/status/<script_id>
```

Response:

```json
{
    "script_id": "script_id",
    "status": "running|finished|not_found",
    ...
}
```

#### Stop Script

```
POST /api/stop/<script_id>
```

Response:

```json
{
    "script_id": "script_id",
    "message": "Script has been stopped"
}
```

## Test Cases

Includes two test cases:

1. **Hello World Example**: A simple Hello World example that generates a lot of logs to test real-time logging functionality
2. **Data Processing Example**: A data processing example using pandas and numpy

### Using Test Cases

```python
from app.code_runner.test_examples import get_examples

# Get Hello World example
hello_world_code = get_examples()['hello_world']['code']

# Use API to run example
import requests
response = requests.post('http://localhost:5000/api/run', json={'code': hello_world_code})
script_id = response.json()['script_id']

# Get logs
logs_response = requests.get(f'http://localhost:5000/api/logs/{script_id}')
logs = logs_response.json()['logs']
print(logs)
```

## Frontend Integration

You can use the following JavaScript code to display logs in real-time on the frontend:

```javascript
function streamLogs(scriptId) {
    const logContainer = document.getElementById('logs');
    const eventSource = new EventSource(`/api/stream-logs/${scriptId}`);
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const logElement = document.createElement('div');
        logElement.textContent = data.log;
        logContainer.appendChild(logElement);
        
        // Auto-scroll to bottom
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // If script has ended, close event source
        if (data.finished) {
            eventSource.close();
        }
    };
    
    eventSource.onerror = function() {
        eventSource.close();
    };
}
```

## Notes

- Running untrusted code may pose security risks, please ensure use in a secure environment
- Dependency installation requires network connection and appropriate permissions
- Long-running scripts may consume significant resources 