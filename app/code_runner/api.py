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

class ScriptResponse(BaseModel):
    script_id: str
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
        "code": "Python code"
    }
    
    Response:
    {
        "script_id": "Script ID",
        "message": "Script has started running"
    }
    """
    try:
        code = code_request.code
        
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
        
        return {
            'script_id': script_id,
            'message': 'Script has started running'
        }
        
    except Exception as e:
        logger.error(f"Error in run script API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running script: {str(e)}")


@app.get("/api/logs/{script_id}", response_model=LogsResponse)
async def get_logs(script_id: str):
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
        
        return {
            'logs': script_logs[script_id]
        }
        
    except Exception as e:
        logger.error(f"Error in get logs API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting logs: {str(e)}")


@app.get("/api/stream-logs/{script_id}")
async def stream_logs(script_id: str):
    """
    Stream Script Logs API
    
    Response: Event stream
    """
    async def generate():
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
                return_code = status.get('return_code')
                yield f"data: {json.dumps({'log': f'Script has ended, return code: {return_code}', 'finished': True})}\n\n"
                break
            
            # Wait for a while
            await asyncio.sleep(0.5)
    
    return StreamingResponse(
        generate(),
        media_type='text/event-stream'
    )


@app.get("/api/status/{script_id}")
async def get_status(script_id: str):
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
        return status
        
    except Exception as e:
        logger.error(f"Error in get status API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@app.post("/api/stop/{script_id}", response_model=ScriptResponse)
async def stop_script(script_id: str):
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
            return {
                'script_id': script_id,
                'message': 'Script has been stopped'
            }
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"Script {script_id} does not exist or has already ended"
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