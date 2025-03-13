"""
SAS代码分块模块

功能：
1. 提取SAS宏，并保留主体
2. 根据输出令牌大小逻辑拆分主体
"""
import re
from typing import List, Dict, Tuple


class SASCodeChunker:
    """SAS代码分块器"""

    def __init__(self, max_token_size: int = 4000):
        """
        初始化SAS代码分块器
        
        Args:
            max_token_size: 每个块的最大令牌大小
        """
        self.max_token_size = max_token_size
        
    def extract_macros(self, code: str, sas_filename: str = "") -> Tuple[Dict[str, str], str]:
        """
        从SAS代码中提取宏，并返回宏字典和剩余的主体代码
        
        Args:
            code: SAS代码
            sas_filename: SAS文件名，用于生成占位符
            
        Returns:
            宏字典和主体代码的元组
        """
        # 正则表达式匹配SAS宏定义
        macro_pattern = r'%macro\s+(\w+)(?:\s*\(.*?\))?\s*;(.*?)%mend\s+\1\s*;'
        macros = {}
        
        # 查找所有宏定义
        for match in re.finditer(macro_pattern, code, re.DOTALL | re.IGNORECASE):
            macro_name = match.group(1)
            macro_body = match.group(2)
            macros[macro_name] = macro_body
        
        # 从原始代码中移除宏定义，并添加占位符
        def replace_with_placeholder(match):
            macro_name = match.group(1)
            placeholder = f"/* {sas_filename}_{macro_name} 宏定义占位符 */"
            return placeholder
        
        main_body = re.sub(macro_pattern, replace_with_placeholder, code, flags=re.DOTALL | re.IGNORECASE)
        
        return macros, main_body
    
    def chunk_code(self, code: str) -> List[str]:
        """
        将代码分块，确保每个块不超过最大令牌大小
        
        Args:
            code: 要分块的代码
            
        Returns:
            代码块列表
        """
        # 简单估计：假设每个字符平均对应0.25个令牌
        chars_per_chunk = int(self.max_token_size * 4)
        
        # 按照分号和换行符分割代码
        statements = re.split(r'(;|\n)', code)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for statement in statements:
            statement_size = len(statement)
            
            # 如果当前块加上新语句会超过限制，则开始新块
            if current_size + statement_size > chars_per_chunk and current_chunk:
                chunks.append(''.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            current_chunk.append(statement)
            current_size += statement_size
        
        # 添加最后一个块
        if current_chunk:
            chunks.append(''.join(current_chunk))
        
        return chunks
    
    def process(self, code: str, sas_filename: str = "") -> Dict:
        """
        处理SAS代码，提取宏并分块主体
        
        Args:
            code: SAS代码
            sas_filename: SAS文件名，用于生成占位符
            
        Returns:
            包含宏和主体块的字典
        """
        macros, main_body = self.extract_macros(code, sas_filename)
        main_body_chunks = self.chunk_code(main_body)
        
        return {
            'macros': macros,
            'main_body_chunks': main_body_chunks
        } 