"""
Python代码合并模块
"""
import re
from typing import Dict, List, Set, Any


class CodeMerger:
    """Python代码合并器"""
    
    def __init__(self):
        """初始化代码合并器"""
        pass
    
    def _extract_imports(self, code: str) -> Set[str]:
        """
        从代码中提取import语句
        
        Args:
            code: Python代码
            
        Returns:
            import语句集合
        """
        # 匹配import语句
        import_pattern = r'^(?:from\s+[\w.]+\s+import\s+(?:[\w.]+(?:\s+as\s+\w+)?(?:\s*,\s*[\w.]+(?:\s+as\s+\w+)?)*)|import\s+(?:[\w.]+(?:\s+as\s+\w+)?(?:\s*,\s*[\w.]+(?:\s+as\s+\w+)?)*))$'
        
        imports = set()
        for line in code.split('\n'):
            line = line.strip()
            if re.match(import_pattern, line):
                imports.add(line)
        
        return imports
    
    def _remove_imports(self, code: str) -> str:
        """
        从代码中移除import语句
        
        Args:
            code: Python代码
            
        Returns:
            移除import语句后的代码
        """
        # 匹配import语句
        import_pattern = r'^(?:from\s+[\w.]+\s+import\s+(?:[\w.]+(?:\s+as\s+\w+)?(?:\s*,\s*[\w.]+(?:\s+as\s+\w+)?)*)|import\s+(?:[\w.]+(?:\s+as\s+\w+)?(?:\s*,\s*[\w.]+(?:\s+as\s+\w+)?)*))$'
        
        lines = []
        for line in code.split('\n'):
            if not re.match(import_pattern, line.strip()):
                lines.append(line)
        
        return '\n'.join(lines)
    
    def merge_functions(self, functions: Dict[str, str]) -> str:
        """
        合并Python函数
        
        Args:
            functions: Python函数字典，键为函数名称，值为函数代码
            
        Returns:
            合并后的Python函数代码
        """
        all_imports = set()
        function_bodies = []
        
        for func_name, func_code in functions.items():
            # 提取import语句
            imports = self._extract_imports(func_code)
            all_imports.update(imports)
            
            # 移除import语句
            func_body = self._remove_imports(func_code)
            function_bodies.append(func_body)
        
        # 合并代码
        merged_code = '\n'.join(sorted(all_imports)) + '\n\n' + '\n\n'.join(function_bodies)
        
        return merged_code
    
    def merge_main_blocks(self, blocks: List[str]) -> str:
        """
        合并Python主体代码块
        
        Args:
            blocks: Python代码块列表
            
        Returns:
            合并后的Python主体代码
        """
        all_imports = set()
        block_bodies = []
        
        for block in blocks:
            # 提取import语句
            imports = self._extract_imports(block)
            all_imports.update(imports)
            
            # 移除import语句
            block_body = self._remove_imports(block)
            block_bodies.append(block_body)
        
        # 合并代码
        merged_code = '\n'.join(sorted(all_imports)) + '\n\n' + '\n\n'.join(block_bodies)
        
        return merged_code
    
    def generate_requirements(self, code: str) -> List[str]:
        """
        从代码中生成requirements.txt内容
        
        Args:
            code: Python代码
            
        Returns:
            requirements.txt内容列表
        """
        # 提取import语句
        imports = self._extract_imports(code)
        
        # 提取包名
        packages = set()
        for import_stmt in imports:
            if import_stmt.startswith('import '):
                # 处理 import package 或 import package as alias
                package = import_stmt.split('import ')[1].split(' as ')[0].split(',')[0].strip()
                base_package = package.split('.')[0]
                packages.add(base_package)
            elif import_stmt.startswith('from '):
                # 处理 from package import ...
                package = import_stmt.split('from ')[1].split(' import')[0].strip()
                base_package = package.split('.')[0]
                packages.add(base_package)
        
        # 过滤标准库
        std_libs = {'os', 'sys', 're', 'math', 'datetime', 'time', 'json', 'csv', 'random', 
                   'collections', 'itertools', 'functools', 'typing', 'pathlib', 'io'}
        packages = {pkg for pkg in packages if pkg not in std_libs}
        
        # 添加常用版本号
        requirements = []
        for pkg in sorted(packages):
            if pkg == 'pandas':
                requirements.append('pandas>=1.3.0')
            elif pkg == 'numpy':
                requirements.append('numpy>=1.20.0')
            elif pkg == 'matplotlib':
                requirements.append('matplotlib>=3.4.0')
            elif pkg == 'sqlalchemy':
                requirements.append('sqlalchemy>=1.4.0')
            elif pkg == 'pyodbc':
                requirements.append('pyodbc>=4.0.30')
            elif pkg == 'pymssql':
                requirements.append('pymssql>=2.2.0')
            elif pkg == 'psycopg2':
                requirements.append('psycopg2-binary>=2.9.0')
            elif pkg == 'pymysql':
                requirements.append('pymysql>=1.0.2')
            elif pkg == 'cx_Oracle':
                requirements.append('cx_Oracle>=8.3.0')
            elif pkg == 'openpyxl':
                requirements.append('openpyxl>=3.0.7')
            elif pkg == 'xlrd':
                requirements.append('xlrd>=2.0.1')
            elif pkg == 'xlwt':
                requirements.append('xlwt>=1.3.0')
            elif pkg == 'scipy':
                requirements.append('scipy>=1.7.0')
            elif pkg == 'statsmodels':
                requirements.append('statsmodels>=0.12.0')
            elif pkg == 'scikit-learn' or pkg == 'sklearn':
                requirements.append('scikit-learn>=1.0.0')
            else:
                requirements.append(f'{pkg}')
        
        return requirements 