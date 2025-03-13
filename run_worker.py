#!/usr/bin/env python
"""
启动Celery worker的脚本
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

if __name__ == '__main__':
    # 导入Celery应用
    from app.celery_app import celery_app
    
    # 启动Celery worker
    celery_app.worker_main(['worker', '--loglevel=info']) 