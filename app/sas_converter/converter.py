"""
SAS到Python转换器主模块
"""
import os
from typing import Dict, List, Any, Optional
from app.sas_analyzer.code_chunker import SASCodeChunker
from app.sas_analyzer.data_source_analyzer import SASDataSourceAnalyzer
from app.sas_analyzer.dependency_analyzer import SASDependencyAnalyzer
from .macro_converter import MacroConverter
from .main_converter import MainConverter
from .code_merger import CodeMerger
from .db_connector import DBConnector
from .dependency_handler import DependencyHandler
from .openai_client import AzureOpenAIClient


class SASConverter:
    """SAS到Python转换器"""
    
    def __init__(self, openai_api_key: Optional[str] = None, azure_openai_api_key: Optional[str] = None):
        """
        初始化SAS转换器
        
        Args:
            openai_api_key: OpenAI API密钥（用于分析）
            azure_openai_api_key: Azure OpenAI API密钥（用于转换）
        """
        # 初始化OpenAI客户端
        self.openai_client = AzureOpenAIClient(api_key=azure_openai_api_key)
        
        # 初始化分析器
        self.code_chunker = SASCodeChunker()
        self.data_source_analyzer = SASDataSourceAnalyzer(openai_api_key=openai_api_key)
        self.dependency_analyzer = SASDependencyAnalyzer(openai_api_key=openai_api_key)
        
        # 初始化转换器
        self.macro_converter = MacroConverter(openai_client=self.openai_client)
        self.main_converter = MainConverter(openai_client=self.openai_client)
        self.code_merger = CodeMerger()
    
    def convert(self, sas_code: str, sas_filename: str = "") -> Dict[str, Any]:
        """
        转换SAS代码为Python代码
        
        Args:
            sas_code: SAS代码
            sas_filename: SAS文件名
            
        Returns:
            转换结果字典
        """
        # 步骤1: 分析SAS代码
        data_source_analysis = self.data_source_analyzer.analyze(sas_code)
        dependency_analysis = self.dependency_analyzer.analyze(sas_code)
        
        # 步骤2: 分块SAS代码
        chunked_code = self.code_chunker.process(sas_code, sas_filename)
        macros = chunked_code['macros']
        main_body_chunks = chunked_code['main_body_chunks']
        
        # 步骤3: 转换宏
        python_functions = self.macro_converter.convert_all_macros(macros)
        
        # 步骤4: 转换主体代码块
        python_blocks = self.main_converter.convert_all_blocks(main_body_chunks)
        
        # 步骤5: 合并代码
        merged_functions = self.code_merger.merge_functions(python_functions)
        merged_main = self.code_merger.merge_main_blocks(python_blocks)
        
        # 步骤6: 处理数据库连接
        db_connector = DBConnector(data_source_analysis)
        db_connection_code = db_connector.generate_db_connections()
        
        # 步骤7: 处理外部依赖
        dependency_handler = DependencyHandler(dependency_analysis)
        
        # 步骤8: 合并所有代码
        full_code = ""
        
        # 添加外部依赖注释
        dependency_comments = dependency_handler.generate_dependency_comments()
        full_code += f"{dependency_comments}\n\n"
        
        # 添加数据库连接代码
        full_code += f"{db_connection_code}\n\n"
        
        # 添加函数代码
        if merged_functions:
            full_code += f"# ===== 函数定义 =====\n{merged_functions}\n\n"
        
        # 添加主体代码
        full_code += f"# ===== 主体代码 =====\n{merged_main}\n"
        
        # 步骤9: 生成requirements.txt
        requirements = self.code_merger.generate_requirements(full_code)
        
        return {
            'python_code': full_code,
            'requirements': requirements,
            'functions': python_functions,
            'main_blocks': python_blocks,
            'data_source_analysis': data_source_analysis,
            'dependency_analysis': dependency_analysis
        }
    
    def save_output(self, result: Dict[str, Any], output_dir: str, base_filename: str) -> None:
        """
        保存转换结果
        
        Args:
            result: 转换结果
            output_dir: 输出目录
            base_filename: 基础文件名
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存Python代码
        python_file = os.path.join(output_dir, f"{base_filename}.py")
        with open(python_file, 'w', encoding='utf-8') as f:
            f.write(result['python_code'])
        
        # 保存requirements.txt
        requirements_file = os.path.join(output_dir, "requirements.txt")
        with open(requirements_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(result['requirements']))
        
        # 保存函数库
        functions_dir = os.path.join(output_dir, "functions")
        os.makedirs(functions_dir, exist_ok=True)
        
        for func_name, func_code in result['functions'].items():
            func_file = os.path.join(functions_dir, f"{func_name}.py")
            with open(func_file, 'w', encoding='utf-8') as f:
                f.write(func_code)
        
        # 保存分析结果
        analysis_dir = os.path.join(output_dir, "analysis")
        os.makedirs(analysis_dir, exist_ok=True)
        
        import json
        
        # 保存数据源分析结果
        data_source_file = os.path.join(analysis_dir, "data_source_analysis.json")
        with open(data_source_file, 'w', encoding='utf-8') as f:
            json.dump(result['data_source_analysis'], f, indent=2)
        
        # 保存依赖分析结果
        dependency_file = os.path.join(analysis_dir, "dependency_analysis.json")
        with open(dependency_file, 'w', encoding='utf-8') as f:
            json.dump(result['dependency_analysis'], f, indent=2) 