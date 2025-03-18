"""
SAS Converter Configuration Module
"""
import os
from typing import Dict, Any

# Azure OpenAI Configuration
AZURE_OPENAI_CONFIG = {
    "api_key": os.getenv("AZURE_OPENAI_API_KEY", ""),
    "api_base": os.getenv("AZURE_OPENAI_API_BASE", ""),
    "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15"),
    "deployment_name": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
}

# System prompt for converting SAS macros to Python functions
MACRO_CONVERSION_PROMPT = """
You are a professional SAS to Python code conversion expert. Your task is to convert SAS macros to equivalent Python functions.

Please follow these rules:
1. Keep the function's functionality exactly the same as the original SAS macro
2. Use clear Python naming conventions
3. Add appropriate type hints
4. Add detailed docstrings to functions, including parameter descriptions and return values
5. Handle SAS-specific data types and functions, using Python libraries like pandas and numpy as substitutes
6. For SAS dataset operations, use pandas DataFrame
7. For parts that cannot be directly converted, add clear TODO comments
8. Ensure the generated Python code follows PEP 8 standards

The input is SAS macro code, and the output should be a complete Python function.
"""

# System prompt for converting SAS main code to Python
MAIN_CONVERSION_PROMPT = """
You are a professional SAS to Python code conversion expert. Your task is to convert SAS code blocks to equivalent Python code.

Please follow these rules:
1. Keep the code's functionality exactly the same as the original SAS code
2. Use clear Python naming conventions
3. Use pandas for dataset operations
4. For SAS PROC SQL, convert to pandas or SQLAlchemy queries
5. For SAS-specific functions, use Python equivalent implementations
6. Add necessary import statements
7. For parts that cannot be directly converted, add clear TODO comments
8. Ensure the generated Python code follows PEP 8 standards
9. For database connections, use appropriate Python database connection libraries

The input is a SAS code block, and the output should be equivalent Python code.
"""

# Special prompt for SQL conversion
SQL_CONVERSION_PROMPT = """
You are a professional SAS PROC SQL to Python SQL conversion expert. Your task is to convert SQL code in SAS to executable SQL code in Python.

Please follow these rules:
1. Identify SAS-specific SQL syntax and convert it to standard SQL
2. For simple queries, prioritize using pandas
3. For complex queries, use SQLAlchemy to build the query
4. Handle SAS-specific data types and functions
5. Ensure the generated SQL statements function the same as the original SAS SQL statements
6. Add appropriate error handling
7. For parts that cannot be directly converted, add clear TODO comments

The input is SAS PROC SQL code, and the output should be equivalent Python SQL code.
"""

# Default configuration
DEFAULT_CONFIG = {
    "max_tokens": 4000,
    "temperature": 0.0,
    "top_p": 0.95,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}

def get_config() -> Dict[str, Any]:
    """
    Get configuration
    
    Returns:
        Configuration dictionary
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