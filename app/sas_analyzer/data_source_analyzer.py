"""
SAS代码数据源分析模块
"""
import re
import os
import json
from typing import Dict, List, Any
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


class SASDataSourceAnalyzer:
    """SAS代码数据源分析器"""
    
    def __init__(self, openai_api_key: str = None, model_name: str = "gpt-4-turbo"):
        """
        初始化SAS数据源分析器
        
        Args:
            openai_api_key: OpenAI API密钥
            model_name: 使用的模型名称
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4-turbo")
        
        if self.openai_api_key:
            self.llm = ChatOpenAI(
                model=self.model_name,
                openai_api_key=self.openai_api_key,
                temperature=0
            )
        else:
            self.llm = None
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """
        分析SAS代码中的数据源
        
        Args:
            code: SAS代码
            
        Returns:
            包含数据源信息的字典
        """
        # 基本分析
        datasets = self._find_datasets(code)
        schemas = self._extract_schemas(code, datasets)
        
        result = {
            'datasets': datasets,
            'schemas': schemas
        }
        
        # 如果有LLM可用，使用AI增强分析
        if self.llm:
            ai_analysis = self._enrich_schemas_with_ai(code, result)
            if ai_analysis:
                result['enriched_schemas'] = ai_analysis
        
        return result
    
    def _find_datasets(self, code: str) -> List[str]:
        """查找代码中使用的所有数据集"""
        datasets = set()
        
        # 查找数据集读取
        input_patterns = [
            r'set\s+([\w\.]+)',
            r'from\s+([\w\.]+)',
            r'merge\s+([\w\.]+)'
        ]
        
        # 查找数据集写入
        output_patterns = [
            r'data\s+([\w\.]+)',
            r'out\s*=\s*([\w\.]+)'
        ]
        
        # 合并所有模式
        all_patterns = input_patterns + output_patterns
        
        for pattern in all_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            datasets.update(matches)
        
        return list(datasets)
    
    def _extract_schemas(self, code: str, datasets: List[str]) -> Dict[str, List[Dict[str, str]]]:
        """
        从代码中提取数据集的模式信息
        
        Args:
            code: SAS代码
            datasets: 数据集列表
            
        Returns:
            数据集模式字典，键为数据集名称，值为字段列表
        """
        schemas = {}
        
        # 查找变量定义
        for dataset in datasets:
            # 尝试查找数据步骤中的变量定义
            dataset_pattern = fr'data\s+{re.escape(dataset)}\s*;(.*?)(?:run|proc|data\s+\w+);'
            dataset_matches = re.findall(dataset_pattern, code, re.DOTALL | re.IGNORECASE)
            
            fields = []
            
            for match in dataset_matches:
                # 查找变量定义
                var_pattern = r'(?:input|attrib|length)\s+([\w\s]+)(?:\$|\d+)?'
                var_matches = re.findall(var_pattern, match, re.IGNORECASE)
                
                for var_match in var_matches:
                    # 分割多个变量
                    vars = re.split(r'\s+', var_match.strip())
                    for var in vars:
                        if var and var.strip():
                            fields.append({
                                'name': var.strip(),
                                'type': 'unknown',  # 默认类型为未知
                                'source': 'code_analysis'
                            })
            
            if fields:
                schemas[dataset] = fields
        
        return schemas
    
    def _enrich_schemas_with_ai(self, code: str, basic_analysis: Dict) -> Dict[str, List[Dict[str, str]]]:
        """
        使用AI增强数据集模式分析
        
        Args:
            code: SAS代码
            basic_analysis: 基本分析结果
            
        Returns:
            增强的数据集模式字典
        """
        if not self.llm:
            return {}
            
        system_prompt = """
        你是一个专业的SAS代码分析专家。请分析以下SAS代码，并提取所有数据集的模式信息。
        
        对于每个数据集，请尽可能提供以下信息：
        1. 数据集名称
        2. 所有字段/变量的名称
        3. 每个字段的数据类型（如果可以推断）
        4. 每个字段的描述或用途（如果可以从代码中推断）
        
        请以JSON格式返回结果，格式如下：
        {
            "dataset_name1": [
                {"name": "field1", "type": "numeric/character/date/etc", "description": "字段描述"},
                {"name": "field2", "type": "numeric/character/date/etc", "description": "字段描述"}
            ],
            "dataset_name2": [
                {"name": "field1", "type": "numeric/character/date/etc", "description": "字段描述"}
            ]
        }
        
        如果无法确定某个字段的类型或描述，请使用"unknown"。
        """
        
        # 准备基本分析结果作为上下文
        context = f"""
        基本分析已发现以下数据集：{basic_analysis['datasets']}
        
        已提取的基本模式信息：{json.dumps(basic_analysis['schemas'], indent=2)}
        
        请基于以上发现并结合你的专业知识，尽可能丰富数据集的模式信息。
        特别是推断字段的数据类型和可能的用途/描述。
        """
        
        # 限制代码长度，避免超出上下文窗口
        max_code_length = 8000
        if len(code) > max_code_length:
            code = code[:max_code_length] + "\n...(代码已截断，仅显示前部分)"
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"{context}\n\n代码:\n```sas\n{code}\n```")
            ]
            
            response = self.llm.invoke(messages)
            
            # 尝试解析JSON响应
            try:
                result = json.loads(response.content)
                return result
            except json.JSONDecodeError:
                # 如果无法解析JSON，尝试从响应中提取JSON
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', response.content, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group(1))
                        return result
                    except json.JSONDecodeError:
                        pass
                
                # 如果仍然无法解析，返回原始响应
                return {"ai_analysis": response.content}
                
        except Exception as e:
            return {"ai_analysis_error": str(e)} 