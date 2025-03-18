"""
Data Source Analyzer Module

Used to analyze data source usage in SAS code
"""
import json
from typing import Dict, List, Any
from .database_analyzer import analyze_database_usage


class DataSourceAnalyzer:
    """Data Source Analyzer"""
    
    def __init__(self, code: str):
        """
        Initialize data source analyzer
        
        Args:
            code: SAS code
        """
        self.code = code
        self.analysis_results = {}
    
    def analyze_databases(self) -> List[Dict[str, Any]]:
        """
        Analyze database usage
        
        Returns:
            List of database usage information
        """
        db_json = analyze_database_usage(self.code)
        return json.loads(db_json)
    
    def analyze_all(self) -> Dict[str, Any]:
        """
        Perform complete data source analysis
        
        Returns:
            All data source analysis results
        """
        # Analyze database usage
        self.analysis_results["databases"] = self.analyze_databases()
        
        # Future extensions for other data source types
        # self.analysis_results["files"] = self.analyze_files()
        # self.analysis_results["api"] = self.analyze_api_calls()
        
        return self.analysis_results
    
    def get_analysis_json(self) -> str:
        """
        Get JSON representation of analysis results
        
        Returns:
            Analysis results in JSON format
        """
        if not self.analysis_results:
            self.analyze_all()
        
        return json.dumps(self.analysis_results, indent=2)
    
    def get_databases_json(self) -> str:
        """
        Get JSON representation of database analysis results
        
        Returns:
            Database analysis results in JSON format
        """
        if "databases" not in self.analysis_results:
            self.analysis_results["databases"] = self.analyze_databases()
        
        return json.dumps(self.analysis_results["databases"], indent=2)


def analyze_data_sources(code: str) -> str:
    """
    Analyze data source usage in SAS code
    
    Args:
        code: SAS code
        
    Returns:
        Data source analysis results in JSON format
    """
    analyzer = DataSourceAnalyzer(code)
    return analyzer.get_analysis_json()


def analyze_databases(code: str) -> str:
    """
    Analyze database usage in SAS code
    
    Args:
        code: SAS code
        
    Returns:
        Database analysis results in JSON format
    """
    analyzer = DataSourceAnalyzer(code)
    return analyzer.get_databases_json() 