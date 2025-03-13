"""
SAS代码复杂度分析模块
"""
import re
from typing import Dict, Any


class SASComplexityAnalyzer:
    """SAS代码复杂度分析器"""
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """
        分析SAS代码的复杂度
        
        Args:
            code: SAS代码
            
        Returns:
            包含复杂度指标的字典
        """
        metrics = {
            'total_lines': self._count_lines(code),
            'code_lines': self._count_code_lines(code),
            'comment_lines': self._count_comment_lines(code),
            'macro_count': self._count_macros(code),
            'proc_count': self._count_procs(code),
            'data_step_count': self._count_data_steps(code),
            'if_count': self._count_if_statements(code),
            'do_loop_count': self._count_do_loops(code),
            'cyclomatic_complexity': self._calculate_cyclomatic_complexity(code)
        }
        
        return metrics
    
    def _count_lines(self, code: str) -> int:
        """计算总行数"""
        return len(code.split('\n'))
    
    def _count_code_lines(self, code: str) -> int:
        """计算代码行数（非空非注释）"""
        lines = code.split('\n')
        code_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('*') and not stripped.startswith('/*'):
                code_lines += 1
                
        return code_lines
    
    def _count_comment_lines(self, code: str) -> int:
        """计算注释行数"""
        # 简单估计，可能不完全准确
        comment_pattern = r'^\s*\*.*?;|^\s*/\*.*?\*/|^\s*/\*|\*/\s*$'
        lines = code.split('\n')
        comment_lines = 0
        
        in_block_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            # 检查是否在块注释中
            if in_block_comment:
                comment_lines += 1
                if '*/' in line:
                    in_block_comment = False
                continue
                
            # 检查是否是注释行
            if stripped.startswith('*') or stripped.startswith('/*'):
                comment_lines += 1
                if '/*' in line and '*/' not in line:
                    in_block_comment = True
                    
        return comment_lines
    
    def _count_macros(self, code: str) -> int:
        """计算宏定义数量"""
        return len(re.findall(r'%macro\s+\w+', code, re.IGNORECASE))
    
    def _count_procs(self, code: str) -> int:
        """计算PROC步骤数量"""
        return len(re.findall(r'proc\s+\w+', code, re.IGNORECASE))
    
    def _count_data_steps(self, code: str) -> int:
        """计算DATA步骤数量"""
        return len(re.findall(r'data\s+[\w\.]+', code, re.IGNORECASE))
    
    def _count_if_statements(self, code: str) -> int:
        """计算IF语句数量"""
        return len(re.findall(r'\bif\b', code, re.IGNORECASE))
    
    def _count_do_loops(self, code: str) -> int:
        """计算DO循环数量"""
        return len(re.findall(r'\bdo\b', code, re.IGNORECASE))
    
    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """
        计算圈复杂度（简化版）
        
        圈复杂度 = 决策点数量 + 1
        决策点包括：if, else, when, do while, do until, select
        """
        decision_points = (
            len(re.findall(r'\bif\b', code, re.IGNORECASE)) +
            len(re.findall(r'\belse\b', code, re.IGNORECASE)) +
            len(re.findall(r'\bwhen\b', code, re.IGNORECASE)) +
            len(re.findall(r'\bdo\s+while\b', code, re.IGNORECASE)) +
            len(re.findall(r'\bdo\s+until\b', code, re.IGNORECASE)) +
            len(re.findall(r'\bselect\b', code, re.IGNORECASE))
        )
        
        return decision_points + 1 