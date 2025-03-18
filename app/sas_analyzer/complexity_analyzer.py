"""
SAS Code Complexity Analysis Module
"""
import re
from typing import Dict, Any


class SASComplexityAnalyzer:
    """SAS Code Complexity Analyzer"""
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze the complexity of SAS code
        
        Args:
            code: SAS code
            
        Returns:
            Dictionary containing complexity metrics
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
        """Count total lines"""
        return len(code.split('\n'))
    
    def _count_code_lines(self, code: str) -> int:
        """Count code lines (non-empty, non-comment)"""
        lines = code.split('\n')
        code_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('*') and not stripped.startswith('/*'):
                code_lines += 1
                
        return code_lines
    
    def _count_comment_lines(self, code: str) -> int:
        """Count comment lines"""
        # Simple estimate, may not be completely accurate
        comment_pattern = r'^\s*\*.*?;|^\s*/\*.*?\*/|^\s*/\*|\*/\s*$'
        lines = code.split('\n')
        comment_lines = 0
        
        in_block_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            # Check if in block comment
            if in_block_comment:
                comment_lines += 1
                if '*/' in line:
                    in_block_comment = False
                continue
                
            # Check if it's a comment line
            if stripped.startswith('*') or stripped.startswith('/*'):
                comment_lines += 1
                if '/*' in line and '*/' not in line:
                    in_block_comment = True
                    
        return comment_lines
    
    def _count_macros(self, code: str) -> int:
        """Count macro definitions"""
        return len(re.findall(r'%macro\s+\w+', code, re.IGNORECASE))
    
    def _count_procs(self, code: str) -> int:
        """Count PROC steps"""
        return len(re.findall(r'proc\s+\w+', code, re.IGNORECASE))
    
    def _count_data_steps(self, code: str) -> int:
        """Count DATA steps"""
        return len(re.findall(r'data\s+[\w\.]+', code, re.IGNORECASE))
    
    def _count_if_statements(self, code: str) -> int:
        """Count IF statements"""
        return len(re.findall(r'\bif\b', code, re.IGNORECASE))
    
    def _count_do_loops(self, code: str) -> int:
        """Count DO loops"""
        return len(re.findall(r'\bdo\b', code, re.IGNORECASE))
    
    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """
        Calculate cyclomatic complexity (simplified)
        
        Cyclomatic complexity = number of decision points + 1
        Decision points include: if, else, when, do while, do until, select
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