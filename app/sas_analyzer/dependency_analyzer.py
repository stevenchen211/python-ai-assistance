"""
SAS代码依赖分析模块
"""
import re
import os
from typing import Dict, List, Set, Any
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


class SASDependencyAnalyzer:
    """SAS代码依赖分析器"""
    
    def __init__(self, openai_api_key: str = None, model_name: str = "gpt-4-turbo"):
        """
        初始化SAS依赖分析器
        
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
        分析SAS代码的依赖关系
        
        Args:
            code: SAS代码
            
        Returns:
            包含依赖关系的字典
        """
        result = {
            'internal_dependencies': self._find_internal_dependencies(code),
            'external_dependencies': self._find_external_dependencies(code),
            'dataset_usage': self._find_dataset_usage(code)
        }
        
        # 如果有LLM可用，使用AI增强分析
        if self.llm:
            ai_analysis = self._analyze_with_ai(code, result)
            result.update(ai_analysis)
        
        return result
    
    def _find_internal_dependencies(self, code: str) -> List[str]:
        """查找内部依赖（如宏调用）"""
        # 查找宏调用
        macro_calls = re.findall(r'%(\w+)(?:\s*\(.*?\))?', code)
        # 排除SAS内置宏
        builtin_macros = {'if', 'then', 'else', 'do', 'end', 'let', 'put', 'global', 'local', 'include'}
        
        return list(set(macro for macro in macro_calls if macro.lower() not in builtin_macros))
    
    def _find_external_dependencies(self, code: str) -> List[str]:
        """查找外部依赖（如%include语句）"""
        # 查找%include语句
        includes = re.findall(r'%include\s+[\'"]?(.*?)[\'"]?;', code, re.IGNORECASE)
        
        # 查找libname语句
        libnames = re.findall(r'libname\s+(\w+)\s+', code, re.IGNORECASE)
        
        return list(set(includes)) + list(set(libnames))
    
    def _find_dataset_usage(self, code: str) -> Dict[str, List[str]]:
        """查找数据集使用情况"""
        # 查找数据集读取
        input_datasets = re.findall(r'set\s+([\w\.]+)', code, re.IGNORECASE)
        input_datasets.extend(re.findall(r'from\s+([\w\.]+)', code, re.IGNORECASE))
        
        # 查找数据集写入
        output_datasets = re.findall(r'data\s+([\w\.]+)', code, re.IGNORECASE)
        output_datasets.extend(re.findall(r'out\s*=\s*([\w\.]+)', code, re.IGNORECASE))
        
        return {
            'input': list(set(input_datasets)),
            'output': list(set(output_datasets))
        }
    
    def _analyze_with_ai(self, code: str, basic_analysis: Dict) -> Dict:
        """
        使用AI增强依赖分析
        
        Args:
            code: SAS代码
            basic_analysis: 基本分析结果
            
        Returns:
            AI增强的分析结果
        """
        if not self.llm:
            return {}
            
        system_prompt = """
        你是一个专业的SAS代码分析专家。请分析以下SAS代码，并提供以下信息：
        1. 代码的主要功能和目的
        2. 所有外部依赖（包括其他程序、宏、库等）
        3. 数据集的使用情况（输入和输出）
        4. 任何潜在的问题或优化建议
        
        请以JSON格式返回结果，包含以下字段：
        {
            "code_purpose": "代码的主要功能描述",
            "external_dependencies": ["依赖1", "依赖2", ...],
            "dataset_usage": {
                "input": ["输入数据集1", "输入数据集2", ...],
                "output": ["输出数据集1", "输出数据集2", ...]
            },
            "potential_issues": ["问题1", "问题2", ...],
            "optimization_suggestions": ["建议1", "建议2", ...]
        }
        """
        
        # 准备基本分析结果作为上下文
        context = f"""
        基本分析已发现以下内容：
        - 内部依赖: {basic_analysis['internal_dependencies']}
        - 外部依赖: {basic_analysis['external_dependencies']}
        - 数据集使用: {basic_analysis['dataset_usage']}
        
        请基于以上发现并结合你的专业知识进行更深入的分析。
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
            import json
            try:
                result = json.loads(response.content)
                return result
            except json.JSONDecodeError:
                # 如果无法解析JSON，返回原始响应
                return {"ai_analysis": response.content}
                
        except Exception as e:
            return {"ai_analysis_error": str(e)} 