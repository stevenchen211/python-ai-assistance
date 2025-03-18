"""
SAS to Python Converter Main Module
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
    """SAS to Python Converter"""
    
    def __init__(self, openai_api_key: Optional[str] = None, azure_openai_api_key: Optional[str] = None):
        """
        Initialize SAS converter
        
        Args:
            openai_api_key: OpenAI API key (for analysis)
            azure_openai_api_key: Azure OpenAI API key (for conversion)
        """
        # Initialize OpenAI client
        self.openai_client = AzureOpenAIClient(api_key=azure_openai_api_key)
        
        # Initialize analyzers
        self.code_chunker = SASCodeChunker()
        self.data_source_analyzer = SASDataSourceAnalyzer(openai_api_key=openai_api_key)
        self.dependency_analyzer = SASDependencyAnalyzer(openai_api_key=openai_api_key)
        
        # Initialize converters
        self.macro_converter = MacroConverter(openai_client=self.openai_client)
        self.main_converter = MainConverter(openai_client=self.openai_client)
        self.code_merger = CodeMerger()
    
    def convert(self, sas_code: str, sas_filename: str = "") -> Dict[str, Any]:
        """
        Convert SAS code to Python code
        
        Args:
            sas_code: SAS code
            sas_filename: SAS filename
            
        Returns:
            Conversion result dictionary
        """
        # Step 1: Analyze SAS code
        data_source_analysis = self.data_source_analyzer.analyze(sas_code)
        dependency_analysis = self.dependency_analyzer.analyze(sas_code)
        
        # Step 2: Chunk SAS code
        chunked_code = self.code_chunker.process(sas_code, sas_filename)
        macros = chunked_code['macros']
        main_body_chunks = chunked_code['main_body_chunks']
        
        # Step 3: Convert macros
        python_functions = self.macro_converter.convert_all_macros(macros)
        
        # Step 4: Convert main body code blocks
        python_blocks = self.main_converter.convert_all_blocks(main_body_chunks)
        
        # Step 5: Merge code
        merged_functions = self.code_merger.merge_functions(python_functions)
        merged_main = self.code_merger.merge_main_blocks(python_blocks)
        
        # Step 6: Handle database connections
        db_connector = DBConnector(data_source_analysis)
        db_connection_code = db_connector.generate_db_connections()
        
        # Step 7: Handle external dependencies
        dependency_handler = DependencyHandler(dependency_analysis)
        
        # Step 8: Merge all code
        full_code = ""
        
        # Add external dependency comments
        dependency_comments = dependency_handler.generate_dependency_comments()
        full_code += f"{dependency_comments}\n\n"
        
        # Add database connection code
        full_code += f"{db_connection_code}\n\n"
        
        # Add function code
        if merged_functions:
            full_code += f"# ===== Function Definitions =====\n{merged_functions}\n\n"
        
        # Add main body code
        full_code += f"# ===== Main Code =====\n{merged_main}\n"
        
        # Step 9: Generate requirements.txt
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
        Save conversion results
        
        Args:
            result: Conversion result
            output_dir: Output directory
            base_filename: Base filename
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save Python code
        python_file = os.path.join(output_dir, f"{base_filename}.py")
        with open(python_file, 'w', encoding='utf-8') as f:
            f.write(result['python_code'])
        
        # Save requirements.txt
        requirements_file = os.path.join(output_dir, "requirements.txt")
        with open(requirements_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(result['requirements']))
        
        # Save function library
        functions_dir = os.path.join(output_dir, "functions")
        os.makedirs(functions_dir, exist_ok=True)
        
        for func_name, func_code in result['functions'].items():
            func_file = os.path.join(functions_dir, f"{func_name}.py")
            with open(func_file, 'w', encoding='utf-8') as f:
                f.write(func_code)
        
        # Save analysis results
        analysis_dir = os.path.join(output_dir, "analysis")
        os.makedirs(analysis_dir, exist_ok=True)
        
        import json
        
        # Save data source analysis results
        data_source_file = os.path.join(analysis_dir, "data_source_analysis.json")
        with open(data_source_file, 'w', encoding='utf-8') as f:
            json.dump(result['data_source_analysis'], f, indent=2)
        
        # Save dependency analysis results
        dependency_file = os.path.join(analysis_dir, "dependency_analysis.json")
        with open(dependency_file, 'w', encoding='utf-8') as f:
            json.dump(result['dependency_analysis'], f, indent=2) 