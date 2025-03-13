"""
SAS主体代码转Python转换器
"""
from typing import Dict, List, Any, Optional
import re
from .openai_client import AzureOpenAIClient
from .config import get_config


class MainConverter:
    """SAS主体代码转Python转换器"""
    
    def __init__(self, openai_client: Optional[AzureOpenAIClient] = None):
        """
        初始化主体代码转换器
        
        Args:
            openai_client: Azure OpenAI客户端
        """
        self.openai_client = openai_client or AzureOpenAIClient()
        self.config = get_config()
        self.main_prompt = self.config["prompts"]["main"]
        self.sql_prompt = self.config["prompts"]["sql"]
    
    def _is_sql_block(self, code_block: str) -> bool:
        """
        判断代码块是否为SQL块
        
        Args:
            code_block: 代码块
            
        Returns:
            是否为SQL块
        """
        return bool(re.search(r'proc\s+sql', code_block, re.IGNORECASE))
    
    def convert_block(self, code_block: str) -> str:
        """
        转换单个代码块
        
        Args:
            code_block: SAS代码块
            
        Returns:
            转换后的Python代码
        """
        # 判断是否为SQL块
        is_sql = self._is_sql_block(code_block)
        system_prompt = self.sql_prompt if is_sql else self.main_prompt
        
        # 使用OpenAI进行转换
        python_code = self.openai_client.generate_completion(
            system_prompt=system_prompt,
            user_prompt=f"请将以下SAS代码转换为Python代码：\n\n```sas\n{code_block}\n```",
            max_tokens=self.config["default"]["max_tokens"],
            temperature=self.config["default"]["temperature"]
        )
        
        return python_code
    
    def convert_all_blocks(self, code_blocks: List[str]) -> List[str]:
        """
        转换所有代码块
        
        Args:
            code_blocks: SAS代码块列表
            
        Returns:
            转换后的Python代码块列表
        """
        python_blocks = []
        
        for block in code_blocks:
            python_block = self.convert_block(block)
            python_blocks.append(python_block)
        
        return python_blocks 