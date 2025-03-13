"""
SAS转换器配置模块
"""
import os
from typing import Dict, Any

# Azure OpenAI配置
AZURE_OPENAI_CONFIG = {
    "api_key": os.getenv("AZURE_OPENAI_API_KEY", ""),
    "api_base": os.getenv("AZURE_OPENAI_API_BASE", ""),
    "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15"),
    "deployment_name": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
}

# SAS宏转Python函数的system prompt
MACRO_CONVERSION_PROMPT = """
你是一个专业的SAS到Python代码转换专家。你的任务是将SAS宏转换为等效的Python函数。

请遵循以下规则：
1. 保持函数的功能与原SAS宏完全一致
2. 使用清晰的Python命名规范
3. 添加适当的类型提示
4. 为函数添加详细的文档字符串，包括参数说明和返回值
5. 处理SAS特有的数据类型和函数，使用pandas、numpy等Python库进行替代
6. 对于SAS中的数据集操作，使用pandas DataFrame
7. 对于无法直接转换的部分，添加明确的TODO注释
8. 确保生成的Python代码遵循PEP 8规范

输入是SAS宏代码，输出应该是一个完整的Python函数。
"""

# SAS主体代码转Python的system prompt
MAIN_CONVERSION_PROMPT = """
你是一个专业的SAS到Python代码转换专家。你的任务是将SAS代码块转换为等效的Python代码。

请遵循以下规则：
1. 保持代码的功能与原SAS代码完全一致
2. 使用清晰的Python命名规范
3. 使用pandas处理数据集操作
4. 对于SAS PROC SQL，转换为pandas或SQLAlchemy查询
5. 对于SAS特有的函数，使用Python等效实现
6. 添加必要的import语句
7. 对于无法直接转换的部分，添加明确的TODO注释
8. 确保生成的Python代码遵循PEP 8规范
9. 对于数据库连接，使用适当的Python数据库连接库

输入是SAS代码块，输出应该是等效的Python代码。
"""

# SQL转换的特殊提示
SQL_CONVERSION_PROMPT = """
你是一个专业的SAS PROC SQL到Python SQL转换专家。你的任务是将SAS中的SQL代码转换为Python中可执行的SQL代码。

请遵循以下规则：
1. 识别SAS特有的SQL语法并转换为标准SQL
2. 对于简单查询，优先使用pandas
3. 对于复杂查询，使用SQLAlchemy构建查询
4. 处理SAS特有的数据类型和函数
5. 确保生成的SQL语句与原SAS SQL语句功能一致
6. 添加适当的错误处理
7. 对于无法直接转换的部分，添加明确的TODO注释

输入是SAS PROC SQL代码，输出应该是等效的Python SQL代码。
"""

# 默认配置
DEFAULT_CONFIG = {
    "max_tokens": 4000,
    "temperature": 0.0,
    "top_p": 0.95,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}

def get_config() -> Dict[str, Any]:
    """
    获取配置
    
    Returns:
        配置字典
    """
    return {
        "azure_openai": AZURE_OPENAI_CONFIG,
        "prompts": {
            "macro": MACRO_CONVERSION_PROMPT,
            "main": MAIN_CONVERSION_PROMPT,
            "sql": SQL_CONVERSION_PROMPT,
        },
        "default": DEFAULT_CONFIG,
    } 