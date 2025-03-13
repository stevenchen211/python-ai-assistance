"""
Azure OpenAI服务客户端
"""
import os
from typing import Dict, List, Any, Optional
import openai
from .config import get_config


class AzureOpenAIClient:
    """Azure OpenAI服务客户端"""
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None, 
                 api_version: Optional[str] = None, deployment_name: Optional[str] = None):
        """
        初始化Azure OpenAI客户端
        
        Args:
            api_key: Azure OpenAI API密钥
            api_base: Azure OpenAI API基础URL
            api_version: Azure OpenAI API版本
            deployment_name: 部署名称
        """
        config = get_config()["azure_openai"]
        
        self.api_key = api_key or config["api_key"]
        self.api_base = api_base or config["api_base"]
        self.api_version = api_version or config["api_version"]
        self.deployment_name = deployment_name or config["deployment_name"]
        
        # 配置OpenAI客户端
        openai.api_type = "azure"
        openai.api_key = self.api_key
        openai.api_base = self.api_base
        openai.api_version = self.api_version
    
    def generate_completion(self, system_prompt: str, user_prompt: str, 
                           max_tokens: int = 4000, temperature: float = 0.0) -> str:
        """
        生成完成
        
        Args:
            system_prompt: 系统提示
            user_prompt: 用户提示
            max_tokens: 最大令牌数
            temperature: 温度
            
        Returns:
            生成的文本
        """
        try:
            response = openai.ChatCompletion.create(
                deployment_id=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API调用失败: {str(e)}")
            return "" 