#!/usr/bin/env python
"""
Script to start Celery worker
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Celery application
from app.celery_app import celery_app

# Start Celery worker
if __name__ == '__main__':
    celery_app.worker_main(["worker", "--loglevel=info"]) 