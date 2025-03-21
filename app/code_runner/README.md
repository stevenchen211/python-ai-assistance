# Python Code Runner

This package provides an API interface for running Python scripts, can solve dependency issues, and provides real-time logging functionality.

## Features

1. **Run Python Scripts**: Run Python scripts through API interface
2. **Dependency Management**: Automatically parse and install dependencies required by scripts
3. **Real-time Logging**: Provides real-time log streaming to monitor script execution status
4. **Script Management**: Manage running scripts, view status and stop execution
5. **Web Interface**: Includes a web interface for running scripts and viewing logs in real-time

## Installation

Make sure you have the required dependencies installed:

```bash
pip install fastapi uvicorn pydantic
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

### Web Interface

The package includes a web interface for running scripts and viewing logs. To access it, start the API service and navigate to `http://localhost:5000` in your browser.

The web interface allows you to:
- Write or paste Python code
- Select from predefined examples
- Run scripts and view real-time logs
- Stop running scripts
- Clear logs

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
    "code_id": "code_id",
    "message": "Script has started running"
}
```

#### Get Logs

```
GET /api/logs/{code_id}
```

Response:

```json
{
    "logs": ["log1", "log2", ...]
}
```

#### Stream Logs

```
GET /api/stream-logs/{code_id}
```

Response: Event stream

#### Get Script Status

```
GET /api/status/{code_id}
```

Response:

```json
{
    "code_id": "code_id",
    "status": "running|finished|not_found",
    ...
}
```

#### Stop Script

```
POST /api/stop/{code_id}
```

Response:

```json
{
    "code_id": "code_id",
    "message": "Script has been stopped"
}
```

#### Get Examples

```
GET /api/examples
```

Response:

```json
{
    "hello_world": {
        "name": "Hello World Example",
        "description": "A simple Hello World example that generates a lot of logs",
        "code": "..."
    },
    "data_processing": {
        "name": "Data Processing Example",
        "description": "A data processing example using pandas and numpy",
        "code": "..."
    }
}
```

#### Get Specific Example

```
GET /api/example/{example_id}
```

Response:

```json
{
    "name": "Example Name",
    "description": "Example description",
    "code": "..."
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
code_id = response.json()['code_id']

# Get logs
logs_response = requests.get(f'http://localhost:5000/api/logs/{code_id}')
logs = logs_response.json()['logs']
print(logs)
```

## Technical Details

### FastAPI Implementation

This package uses FastAPI for the API interface, which provides:
- Modern, fast API framework based on standard Python type hints
- Automatic API documentation (Swagger UI) at `/docs`
- High performance with async support
- Easy to use and extend

### Real-time Logging

The real-time logging is implemented using Server-Sent Events (SSE), which allows the server to push updates to the client in real-time.

## Notes

- Running untrusted code may pose security risks, please ensure use in a secure environment
- Dependency installation requires network connection and appropriate permissions
- Long-running scripts may consume significant resources

## New Feature: SAS Database Analysis Tool

This package adds SAS code database analysis functionality that can analyze database connections and table operations in SAS code.

### Main Features

- Identifies multiple database types: Oracle, SQL Server, BigQuery, Teradata, etc.
- Parses SAS variable references (such as `&var_name`)
- Analyzes table operations: SELECT, INSERT, UPDATE, DELETE, CREATE VIEW, SELECT INTO, etc.
- Supports command line tools and API calls

### Usage

**Command line tool**:
```bash
python analyze_sas.py [options] [SAS_file_path]
```

**API call**:
```python
from app.code_runner.data_source_analyzer import analyze_databases

result = analyze_databases(sas_code)
```

For detailed information, please refer to the [Database Analysis Tool Documentation](./README_DATABASE_ANALYZER.md).