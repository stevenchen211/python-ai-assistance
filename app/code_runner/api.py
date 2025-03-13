"""
API Interface Module

Provides HTTP API interface to run Python scripts and get real-time logs
"""
import os
import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from .script_runner import ScriptRunner
from .test_examples import get_examples

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(title="Python Code Runner API", 
              description="API for running Python scripts with real-time logging")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create script runner
script_runner = ScriptRunner()

# Dictionary to store logs
script_logs = {}

# Define request and response models
class CodeRequest(BaseModel):
    code: str
    skip_dependencies: bool = False

class ScriptResponse(BaseModel):
    code_id: str
    message: str

class LogsResponse(BaseModel):
    logs: List[str]

class ErrorResponse(BaseModel):
    error: str

# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

# Root endpoint redirects to index.html
@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))

# Get examples endpoint
@app.get("/api/examples")
async def get_all_examples():
    """
    Get all example codes
    
    Response:
    {
        "hello_world": {
            "name": "Hello World Example",
            "description": "...",
            "code": "..."
        },
        "data_processing": {
            "name": "Data Processing Example",
            "description": "...",
            "code": "..."
        }
    }
    """
    return get_examples()

# Get specific example endpoint
@app.get("/api/example/{example_id}")
async def get_example(example_id: str):
    """
    Get specific example code
    
    Response:
    {
        "name": "Example Name",
        "description": "...",
        "code": "..."
    }
    """
    examples = get_examples()
    if example_id not in examples:
        raise HTTPException(status_code=404, detail=f"Example {example_id} not found")
    
    return examples[example_id]

@app.post("/api/run", response_model=ScriptResponse)
async def run_script(code_request: CodeRequest):
    """
    Run Python Script API
    
    Request body:
    {
        "code": "Python code",
        "skip_dependencies": false
    }
    
    Response:
    {
        "code_id": "Code ID",
        "message": "Script has started running"
    }
    """
    try:
        code = code_request.code
        skip_dependencies = code_request.skip_dependencies
        
        # Initialize log list
        code_id = None
        
        def log_callback(message):
            nonlocal code_id
            if code_id:
                if code_id not in script_logs:
                    script_logs[code_id] = []
                script_logs[code_id].append(message)
        
        # Run script
        code_id = script_runner.run_script(code, log_callback, skip_dependencies)
        
        # Initialize logs
        if code_id not in script_logs:
            script_logs[code_id] = []
        
        return {
            'code_id': code_id,
            'message': 'Script has started running'
        }
        
    except Exception as e:
        logger.error(f"Error in run script API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running script: {str(e)}")


@app.get("/api/logs/{code_id}", response_model=LogsResponse)
async def get_logs(code_id: str):
    """
    Get Script Logs API
    
    Response:
    {
        "logs": ["Log 1", "Log 2", ...]
    }
    """
    try:
        # Get new logs
        new_logs = script_runner.get_logs(code_id)
        
        # Add to log storage
        if code_id not in script_logs:
            script_logs[code_id] = []
        
        script_logs[code_id].extend(new_logs)
        
        return {
            'logs': script_logs[code_id]
        }
        
    except Exception as e:
        logger.error(f"Error in get logs API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting logs: {str(e)}")


@app.get("/api/stream-logs/{code_id}")
async def stream_logs(code_id: str):
    """
    Stream Script Logs API
    
    Response: Event stream
    """
    async def generate():
        # Initialize log index
        if code_id not in script_logs:
            script_logs[code_id] = []
        
        log_index = 0
        
        # 初始等待时间短，提高响应速度
        wait_time = 0.1
        
        while True:
            try:
                # Get new logs
                new_logs = script_runner.get_logs(code_id)
                
                # 有新日志时立即发送
                has_new_logs = len(new_logs) > 0
                
                # Add to log storage
                script_logs[code_id].extend(new_logs)
                
                # Send new logs
                current_logs = script_logs[code_id]
                while log_index < len(current_logs):
                    log = current_logs[log_index]
                    log_index += 1
                    yield f"data: {json.dumps({'log': log})}\n\n"
                
                # Check if script has ended
                status = script_runner.get_script_status(code_id)
                if status['status'] == 'finished' or status['status'] == 'not_found':
                    return_code = status.get('return_code', 0)
                    yield f"data: {json.dumps({'log': f'Script has ended, return code: {return_code}', 'finished': True})}\n\n"
                    break
                
                # 动态调整等待时间：有日志时快速响应，无日志时逐渐增加等待时间
                if has_new_logs:
                    # 有新日志，保持较短的等待时间
                    wait_time = 0.1
                else:
                    # 无新日志，逐渐增加等待时间，但不超过0.5秒
                    wait_time = min(wait_time * 1.2, 0.5)
                
                # Wait for a while
                await asyncio.sleep(wait_time)
            except Exception as e:
                logger.error(f"Error in stream logs: {str(e)}")
                yield f"data: {json.dumps({'log': f'Error in stream logs: {str(e)}', 'finished': True})}\n\n"
                break
    
    return StreamingResponse(
        generate(),
        media_type='text/event-stream'
    )


@app.get("/api/status/{code_id}")
async def get_status(code_id: str):
    """
    Get Script Status API
    
    Response:
    {
        "code_id": "Code ID",
        "status": "running|finished|not_found",
        ...
    }
    """
    try:
        status = script_runner.get_script_status(code_id)
        # Replace script_id with code_id in the response
        if 'script_id' in status:
            status['code_id'] = status.pop('script_id')
        return status
        
    except Exception as e:
        logger.error(f"Error in get status API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@app.post("/api/stop/{code_id}", response_model=ScriptResponse)
async def stop_script(code_id: str):
    """
    Stop Script API
    
    Response:
    {
        "code_id": "Code ID",
        "message": "Script has been stopped"
    }
    """
    try:
        success = script_runner.stop_script(code_id)
        
        if success:
            return {
                'code_id': code_id,
                'message': 'Script has been stopped'
            }
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"Script {code_id} does not exist or has already ended"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in stop script API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error stopping script: {str(e)}")


def start_api(host='0.0.0.0', port=5000, debug=False, static_dir=None):
    """
    Start API service
    
    Args:
        host: Host address
        port: Port number
        debug: Whether to enable debug mode
        static_dir: Static files directory path
    """
    # Mount static files if provided
    if static_dir:
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    else:
        # Use default static directory
        default_static_dir = os.path.join(os.path.dirname(__file__), "static")
        if os.path.exists(default_static_dir):
            app.mount("/static", StaticFiles(directory=default_static_dir), name="static")
    
    uvicorn.run(app, host=host, port=port, log_level="debug" if debug else "info")


if __name__ == '__main__':
    start_api(debug=True)