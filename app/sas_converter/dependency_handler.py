"""
SAS外部依赖处理模块
"""
from typing import Dict, List, Any, Optional


class DependencyHandler:
    """SAS外部依赖处理器"""
    
    def __init__(self, dependency_analysis: Optional[Dict[str, Any]] = None):
        """
        初始化依赖处理器
        
        Args:
            dependency_analysis: 依赖分析结果
        """
        self.dependency_analysis = dependency_analysis or {}
    
    def generate_dependency_comments(self) -> str:
        """
        生成依赖注释
        
        Returns:
            依赖注释代码
        """
        if not self.dependency_analysis or 'external_dependencies' not in self.dependency_analysis:
            return "# 未检测到外部依赖"
        
        external_deps = self.dependency_analysis.get('external_dependencies', [])
        
        if not external_deps:
            return "# 未检测到外部依赖"
        
        comments = ["# ===== 外部依赖 =====", "# 以下是SAS代码中使用的外部依赖，需要手动处理"]
        
        for dep in external_deps:
            comments.append(f"# TODO: 处理外部依赖 - {dep}")
        
        comments.append("# ==================")
        
        return "\n".join(comments)
    
    def mark_dependencies_in_code(self, code: str) -> str:
        """
        在代码中标记依赖
        
        Args:
            code: Python代码
            
        Returns:
            标记依赖后的代码
        """
        if not self.dependency_analysis or 'external_dependencies' not in self.dependency_analysis:
            return code
        
        external_deps = self.dependency_analysis.get('external_dependencies', [])
        
        if not external_deps:
            return code
        
        # 添加依赖注释到代码开头
        dependency_comments = self.generate_dependency_comments()
        
        return f"{dependency_comments}\n\n{code}" 