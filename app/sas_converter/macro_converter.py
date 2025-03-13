"""
SAS宏转Python函数转换器
"""
from typing import Dict, List, Any, Optional
from .openai_client import AzureOpenAIClient
from .config import get_config


class MacroConverter:
    """SAS宏转Python函数转换器"""
    
    def __init__(self, openai_client: Optional[AzureOpenAIClient] = None):
        """
        初始化宏转换器
        
        Args:
            openai_client: Azure OpenAI客户端
        """
        self.openai_client = openai_client or AzureOpenAIClient()
        self.config = get_config()
        self.system_prompt = self.config["prompts"]["macro"]
    
    def convert_macro(self, macro_name: str, macro_body: str) -> str:
        """
        转换单个SAS宏为Python函数
        
        Args:
            macro_name: 宏名称
            macro_body: 宏主体代码
            
        Returns:
            转换后的Python函数代码
        """
        # 构建完整的宏代码
        full_macro = f"%macro {macro_name};\n{macro_body}\n%mend {macro_name};"
        
        # 使用OpenAI进行转换
        python_function = self.openai_client.generate_completion(
            system_prompt=self.system_prompt,
            user_prompt=f"请将以下SAS宏转换为Python函数：\n\n```sas\n{full_macro}\n```",
            max_tokens=self.config["default"]["max_tokens"],
            temperature=self.config["default"]["temperature"]
        )
        
        return python_function
    
    def convert_all_macros(self, macros: Dict[str, str]) -> Dict[str, str]:
        """
        转换所有SAS宏为Python函数
        
        Args:
            macros: 宏字典，键为宏名称，值为宏主体代码
            
        Returns:
            转换后的Python函数字典，键为函数名称，值为函数代码
        """
        python_functions = {}
        
        for macro_name, macro_body in macros.items():
            python_function = self.convert_macro(macro_name, macro_body)
            python_functions[macro_name] = python_function
        
        return python_functions 