"""
SAS代码分析Celery任务
"""
import os
import json
import logging
from typing import Dict, Any, Optional

from app.celery_app import celery_app
from app.sas_analyzer.code_chunker import SASCodeChunker
from app.sas_analyzer.complexity_analyzer import SASComplexityAnalyzer
from app.sas_analyzer.dependency_analyzer import SASDependencyAnalyzer
from app.sas_analyzer.data_source_analyzer import SASDataSourceAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@celery_app.task(name='sas_code_analysis.analyze_code')
def analyze_code(code: str, max_token_size: int = 4000) -> Dict[str, Any]:
    """
    分析SAS代码的Celery任务
    
    Args:
        code: 要分析的SAS代码
        max_token_size: 代码分块的最大令牌大小
        
    Returns:
        包含分析结果的字典
    """
    logger.info("开始SAS代码分析任务")
    
    try:
        # 1. 代码分块
        logger.info("执行代码分块")
        chunker = SASCodeChunker(max_token_size=max_token_size)
        chunking_result = chunker.process(code)
        
        # 2. 代码复杂度分析
        logger.info("执行代码复杂度分析")
        complexity_analyzer = SASComplexityAnalyzer()
        complexity_result = complexity_analyzer.analyze(code)
        
        # 3. 依赖分析
        logger.info("执行依赖分析")
        dependency_analyzer = SASDependencyAnalyzer(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name=os.getenv("OPENAI_MODEL")
        )
        dependency_result = dependency_analyzer.analyze(code)
        
        # 4. 数据源分析
        logger.info("执行数据源分析")
        data_source_analyzer = SASDataSourceAnalyzer(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name=os.getenv("OPENAI_MODEL")
        )
        data_source_result = data_source_analyzer.analyze(code)
        
        # 合并所有结果
        result = {
            "chunking": chunking_result,
            "complexity": complexity_result,
            "dependencies": dependency_result,
            "data_sources": data_source_result
        }
        
        logger.info("SAS代码分析任务完成")
        return result
        
    except Exception as e:
        logger.error(f"SAS代码分析任务失败: {str(e)}", exc_info=True)
        return {"error": str(e)}


@celery_app.task(name='sas_code_analysis.analyze_file')
def analyze_file(file_path: str, max_token_size: int = 4000) -> Dict[str, Any]:
    """
    分析SAS代码文件的Celery任务
    
    Args:
        file_path: SAS代码文件路径
        max_token_size: 代码分块的最大令牌大小
        
    Returns:
        包含分析结果的字典
    """
    logger.info(f"开始分析SAS代码文件: {file_path}")
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 调用代码分析任务
        result = analyze_code(code, max_token_size)
        
        # 添加文件信息
        result["file_info"] = {
            "path": file_path,
            "name": os.path.basename(file_path),
            "size": os.path.getsize(file_path),
            "last_modified": os.path.getmtime(file_path)
        }
        
        return result
        
    except Exception as e:
        logger.error(f"SAS代码文件分析任务失败: {str(e)}", exc_info=True)
        return {"error": str(e), "file_path": file_path}


@celery_app.task(name='sas_code_analysis.analyze_directory')
def analyze_directory(directory_path: str, file_pattern: str = "*.sas", max_token_size: int = 4000) -> Dict[str, Any]:
    """
    分析目录中所有SAS代码文件的Celery任务
    
    Args:
        directory_path: 目录路径
        file_pattern: 文件匹配模式
        max_token_size: 代码分块的最大令牌大小
        
    Returns:
        包含分析结果的字典
    """
    import glob
    
    logger.info(f"开始分析目录中的SAS代码文件: {directory_path}")
    
    try:
        # 查找所有匹配的文件
        file_pattern_path = os.path.join(directory_path, file_pattern)
        files = glob.glob(file_pattern_path)
        
        logger.info(f"找到 {len(files)} 个SAS文件")
        
        results = {}
        
        # 分析每个文件
        for file_path in files:
            file_name = os.path.basename(file_path)
            logger.info(f"分析文件: {file_name}")
            
            # 调用文件分析任务
            file_result = analyze_file.delay(file_path, max_token_size)
            results[file_name] = file_result.id
        
        return {
            "directory": directory_path,
            "file_count": len(files),
            "task_ids": results
        }
        
    except Exception as e:
        logger.error(f"目录分析任务失败: {str(e)}", exc_info=True)
        return {"error": str(e), "directory_path": directory_path} 