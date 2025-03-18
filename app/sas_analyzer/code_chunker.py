"""
SAS Code Chunker Module

功能：
1. 提取SAS宏，并保留主体
2. 根据输出令牌大小逻辑拆分主体
"""
import re
from typing import List, Dict, Tuple, Any


class SASCodeChunker:
    """SAS Code Chunker"""

    def __init__(self, max_token_size: int = 4000):
        """
        Initialize SAS code chunker
        
        Args:
            max_token_size: Maximum token size for each chunk
        """
        self.max_token_size = max_token_size
        
    def extract_macros(self, code: str, filename: str = "") -> Tuple[List[Dict[str, Any]], str]:
        """
        Extract macro definitions from SAS code
        
        Args:
            code: SAS code
            filename: SAS file name for generating placeholders
            
        Returns:
            Tuple containing (list of macro definitions, main body code with macros removed)
        """
        macro_pattern = r'%macro\s+(\w+).*?%mend\s+\1\s*;'
        macros = []
        
        # Find all macros
        main_body = code
        for idx, match in enumerate(re.finditer(macro_pattern, code, re.IGNORECASE | re.DOTALL)):
            macro_name = match.group(1)
            macro_code = match.group(0)
            
            # Create placeholder
            placeholder = f"/* MACRO_{idx}_{macro_name}_{filename} */"
            
            # Replace macro with placeholder in main body
            main_body = main_body.replace(macro_code, placeholder)
            
            # Store macro information
            macros.append({
                'name': macro_name,
                'code': macro_code,
                'placeholder': placeholder,
                'index': idx
            })
        
        return macros, main_body
    
    def chunk_code(self, code: str) -> List[str]:
        """
        Chunk code ensuring each chunk does not exceed maximum token size
        
        Args:
            code: Code to chunk
            
        Returns:
            List of code chunks
        """
        # Simple estimate: assume each character corresponds to 0.25 tokens
        chars_per_chunk = int(self.max_token_size * 4)
        
        # Split code by semicolons and newlines
        statements = re.split(r'(;|\n)', code)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for statement in statements:
            statement_size = len(statement)
            
            # If current chunk plus new statement exceeds limit, start new chunk
            if current_size + statement_size > chars_per_chunk and current_chunk:
                chunks.append(''.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            current_chunk.append(statement)
            current_size += statement_size
        
        # Add the last chunk
        if current_chunk:
            chunks.append(''.join(current_chunk))
        
        return chunks
    
    def process(self, code: str, sas_filename: str = "") -> Dict:
        """
        Process SAS code, extract macros and chunk main body
        
        Args:
            code: SAS code
            sas_filename: SAS file name for generating placeholders
            
        Returns:
            Dictionary containing macros and main body chunks
        """
        macros, main_body = self.extract_macros(code, sas_filename)
        main_body_chunks = self.chunk_code(main_body)
        
        return {
            'macros': macros,
            'main_body_chunks': main_body_chunks
        } 