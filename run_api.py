#!/usr/bin/env python
"""
SAS代码分析API服务器
"""
import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from celery.result import AsyncResult

# 加载环境变量
load_dotenv()

# 导入Celery应用和任务
from app.celery_app import celery_app
from app.tasks import analyze_code, analyze_file, analyze_directory

# 创建FastAPI应用
app = FastAPI(
    title="SAS代码分析API",
    description="用于分析SAS代码的API服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义请求模型
class CodeAnalysisRequest(BaseModel):
    code: str
    max_token_size: int = 4000

class FileAnalysisRequest(BaseModel):
    file_path: str
    max_token_size: int = 4000

class DirectoryAnalysisRequest(BaseModel):
    directory_path: str
    file_pattern: str = "*.sas"
    max_token_size: int = 4000

# 定义响应模型
class TaskResponse(BaseModel):
    task_id: str
    status: str = "PENDING"
    message: str = "任务已提交"

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# API路由
@app.post("/api/analyze/code", response_model=TaskResponse)
async def api_analyze_code(request: CodeAnalysisRequest):
    """
    分析SAS代码
    """
    try:
        # 提交Celery任务
        task = analyze_code.delay(request.code, request.max_token_size)
        return TaskResponse(task_id=task.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/file", response_model=TaskResponse)
async def api_analyze_file(request: FileAnalysisRequest):
    """
    分析SAS代码文件
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=404, detail=f"文件不存在: {request.file_path}")
            
        # 提交Celery任务
        task = analyze_file.delay(request.file_path, request.max_token_size)
        return TaskResponse(task_id=task.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/directory", response_model=TaskResponse)
async def api_analyze_directory(request: DirectoryAnalysisRequest):
    """
    分析目录中的SAS代码文件
    """
    try:
        # 检查目录是否存在
        if not os.path.isdir(request.directory_path):
            raise HTTPException(status_code=404, detail=f"目录不存在: {request.directory_path}")
            
        # 提交Celery任务
        task = analyze_directory.delay(
            request.directory_path, 
            request.file_pattern, 
            request.max_token_size
        )
        return TaskResponse(task_id=task.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    获取任务状态
    """
    try:
        # 获取任务结果
        task_result = AsyncResult(task_id, app=celery_app)
        
        response = TaskStatusResponse(
            task_id=task_id,
            status=task_result.status
        )
        
        # 如果任务完成，返回结果
        if task_result.ready():
            if task_result.successful():
                response.result = task_result.result
            else:
                response.status = "FAILURE"
                response.error = str(task_result.result)
                
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # 启动FastAPI服务器
    uvicorn.run(
        "run_api:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    ) 