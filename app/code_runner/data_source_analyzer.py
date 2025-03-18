"""
Data Source Analyzer Module

用于分析SAS代码中的数据源使用情况
"""
import json
from typing import Dict, List, Any
from .database_analyzer import analyze_database_usage


class DataSourceAnalyzer:
    """数据源分析器"""
    
    def __init__(self, code: str):
        """
        初始化数据源分析器
        
        Args:
            code: SAS代码
        """
        self.code = code
        self.analysis_results = {}
    
    def analyze_databases(self) -> List[Dict[str, Any]]:
        """
        分析数据库使用情况
        
        Returns:
            数据库使用信息列表
        """
        db_json = analyze_database_usage(self.code)
        return json.loads(db_json)
    
    def analyze_all(self) -> Dict[str, Any]:
        """
        执行完整的数据源分析
        
        Returns:
            所有数据源分析结果
        """
        # 分析数据库使用情况
        self.analysis_results["databases"] = self.analyze_databases()
        
        # 未来可以添加其他数据源分析功能
        # self.analysis_results["files"] = self.analyze_files()
        # self.analysis_results["api"] = self.analyze_api_calls()
        
        return self.analysis_results
    
    def get_analysis_json(self) -> str:
        """
        获取分析结果的JSON表示
        
        Returns:
            JSON格式的分析结果
        """
        if not self.analysis_results:
            self.analyze_all()
        
        return json.dumps(self.analysis_results, indent=2)
    
    def get_databases_json(self) -> str:
        """
        获取数据库分析结果的JSON表示
        
        Returns:
            JSON格式的数据库分析结果
        """
        if "databases" not in self.analysis_results:
            self.analysis_results["databases"] = self.analyze_databases()
        
        return json.dumps(self.analysis_results["databases"], indent=2)


def analyze_data_sources(code: str) -> str:
    """
    分析SAS代码中的数据源使用情况
    
    Args:
        code: SAS代码
        
    Returns:
        JSON格式的数据源分析结果
    """
    analyzer = DataSourceAnalyzer(code)
    return analyzer.get_analysis_json()


def analyze_databases(code: str) -> str:
    """
    分析SAS代码中的数据库使用情况
    
    Args:
        code: SAS代码
        
    Returns:
        JSON格式的数据库分析结果
    """
    analyzer = DataSourceAnalyzer(code)
    return analyzer.get_databases_json() 