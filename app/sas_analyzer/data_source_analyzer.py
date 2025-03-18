"""
SAS Data Source Analyzer Module
"""
import re
import json
from typing import Dict, List, Any, Optional
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models import AzureChatOpenAI


class SASDataSourceAnalyzer:
    """SAS Code Data Source Analyzer"""
    
    def __init__(self, openai_api_key: str = None, model_name: str = "gpt-4-turbo"):
        """
        Initialize data source analyzer
        
        Args:
            openai_api_key: OpenAI API key
            model_name: Model name for AI analysis
        """
        self.llm = None
        
        # Initialize AI model if API key is provided
        if openai_api_key:
            try:
                import os
                azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
                api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
                deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", model_name)
                
                self.llm = AzureChatOpenAI(
                    openai_api_key=openai_api_key,
                    azure_endpoint=azure_endpoint,
                    api_version=api_version,
                    deployment_name=deployment_name,
                    temperature=0.0
                )
            except ImportError:
                print("LangChain or OpenAI packages not installed. AI enhancement unavailable.")
            except Exception as e:
                print(f"Error initializing AI model: {str(e)}")
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze data sources in SAS code
        
        Args:
            code: SAS code
            
        Returns:
            Analysis results dictionary
        """
        # Find datasets used in the code
        datasets = self._find_datasets(code)
        
        # Extract basic schema information
        schemas = self._extract_schemas(code, datasets)
        
        # Basic analysis results
        basic_analysis = {
            'datasets': datasets,
            'schemas': schemas
        }
        
        # Enhance with AI if available
        if self.llm:
            try:
                enhanced_schemas = self._enrich_schemas_with_ai(code, basic_analysis)
                basic_analysis['enhanced_schemas'] = enhanced_schemas
            except Exception as e:
                basic_analysis['ai_analysis_error'] = str(e)
        
        return basic_analysis
    
    def _find_datasets(self, code: str) -> List[str]:
        """
        Find datasets used in SAS code
        
        Args:
            code: SAS code
            
        Returns:
            List of dataset names
        """
        # Various patterns to detect dataset references
        patterns = [
            r'set\s+([\w\.]+)',  # SET statement
            r'data\s+([\w\.]+)',  # DATA statement
            r'from\s+([\w\.]+)',  # FROM clause in SQL
            r'table\s*=\s*([\w\.]+)',  # TABLE= option
            r'out\s*=\s*([\w\.]+)'  # OUT= option
        ]
        
        datasets = set()
        
        for pattern in patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            for match in matches:
                # Normalize dataset name and add to set
                dataset_name = match.strip()
                if dataset_name and not dataset_name.startswith('%'):
                    datasets.add(dataset_name)
        
        return list(datasets)
    
    def _extract_schemas(self, code: str, datasets: List[str]) -> Dict[str, List[Dict[str, str]]]:
        """
        Extract basic schema information from SAS code
        
        Args:
            code: SAS code
            datasets: List of dataset names
            
        Returns:
            Dictionary mapping dataset names to schema information
        """
        schemas = {}
        
        # Very simple variable extraction, not comprehensive
        for dataset in datasets:
            # Try to find variables defined or used with this dataset
            dataset_pattern = fr'{dataset}\.([\w]+)'
            var_matches = re.findall(dataset_pattern, code, re.IGNORECASE)
            
            if var_matches:
                unique_vars = list(set(var_matches))
                schemas[dataset] = [{"name": var, "type": "unknown", "description": ""} for var in unique_vars]
        
        return schemas
    
    def _enrich_schemas_with_ai(self, code: str, basic_analysis: Dict) -> Dict[str, List[Dict[str, str]]]:
        """
        Enhance dataset schema analysis using AI
        
        Args:
            code: SAS code
            basic_analysis: Basic analysis results
            
        Returns:
            Enhanced dataset schema dictionary
        """
        if not self.llm:
            return {}
            
        system_prompt = """
        You are a professional SAS code analysis expert. Please analyze the following SAS code and extract schema information for all datasets.
        
        For each dataset, please provide the following information if possible:
        1. Dataset name
        2. All field/variable names
        3. Data type of each field (if can be inferred)
        4. Description or purpose of each field (if can be inferred from the code)
        
        Please return the results in JSON format as follows:
        {
            "dataset_name1": [
                {"name": "field1", "type": "numeric/character/date/etc", "description": "field description"},
                {"name": "field2", "type": "numeric/character/date/etc", "description": "field description"}
            ],
            "dataset_name2": [
                {"name": "field1", "type": "numeric/character/date/etc", "description": "field description"}
            ]
        }
        
        If you cannot determine the type or description of a field, please use "unknown".
        """
        
        # Prepare basic analysis results as context
        context = f"""
        Basic analysis has discovered the following datasets: {basic_analysis['datasets']}
        
        Basic schema information extracted: {json.dumps(basic_analysis['schemas'], indent=2)}
        
        Based on the above findings and your professional knowledge, please enrich the dataset schema information as much as possible.
        Particularly, infer data types of fields and their possible purpose/description.
        """
        
        # Limit code length to avoid exceeding context window
        max_code_length = 8000
        if len(code) > max_code_length:
            code = code[:max_code_length] + "\n...(code truncated, only showing the beginning)"
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"{context}\n\nCode:\n```sas\n{code}\n```")
            ]
            
            response = self.llm.invoke(messages)
            
            # Try to parse JSON response
            try:
                result = json.loads(response.content)
                return result
            except json.JSONDecodeError:
                # If cannot parse JSON, try to extract JSON from response
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', response.content, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group(1))
                        return result
                    except json.JSONDecodeError:
                        pass
                
                # If still cannot parse, return the original response
                return {"ai_analysis": response.content}
                
        except Exception as e:
            return {"ai_analysis_error": str(e)} 