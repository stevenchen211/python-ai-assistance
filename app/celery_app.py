"""
Celery应用程序配置
"""
import os
from celery import Celery
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建Celery实例
celery_app = Celery(
    'sas_code_analysis',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    include=['app.tasks']
)

# 配置Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

if __name__ == '__main__':
    celery_app.start() 