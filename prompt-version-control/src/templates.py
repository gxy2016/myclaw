"""
模板引擎模块
支持变量替换、条件逻辑等模板功能
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ValidationError:
    """验证错误"""
    variable: str
    message: str


class TemplateEngine:
    """提示词模板引擎"""
    
    def __init__(self):
        # 变量模式：{{variable_name}}
        self.variable_pattern = re.compile(r'\{\{(\w+)\}\}')
        # 条件模式：{% if variable %}...{% endif %}
        self.if_pattern = re.compile(r'\{%\s*if\s+(\w+)\s*%\}(.*?)\{%\s*endif\s*%\}', re.DOTALL)
        # 可选变量模式：{{variable_name|default_value}}
        self.optional_pattern = re.compile(r'\{\{(\w+)\|([^}]+)\}\}')
    
    def render(self, prompt: str, variables: Dict[str, Any]) -> str:
        """
        渲染模板，替换变量
        
        Args:
            prompt: 模板字符串
            variables: 变量字典
            
        Returns:
            渲染后的字符串
        """
        result = prompt
        
        # 处理条件逻辑
        result = self._process_conditionals(result, variables)
        
        # 处理可选变量（带默认值）
        result = self._process_optional_variables(result, variables)
        
        # 处理必需变量
        result = self._process_required_variables(result, variables)
        
        return result
    
    def _process_conditionals(self, text: str, variables: Dict[str, Any]) -> str:
        """处理条件逻辑"""
        def replace_if(match):
            var_name = match.group(1)
            content = match.group(2)
            
            # 如果变量存在且为真，保留内容
            if var_name in variables and variables[var_name]:
                return content
            return ""
        
        return self.if_pattern.sub(replace_if, text)
    
    def _process_optional_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """处理可选变量（带默认值）"""
        def replace_optional(match):
            var_name = match.group(1)
            default_value = match.group(2)
            
            return str(variables.get(var_name, default_value))
        
        return self.optional_pattern.sub(replace_optional, text)
    
    def _process_required_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """处理必需变量"""
        def replace_required(match):
            var_name = match.group(1)
            
            if var_name not in variables:
                # 保留原变量标记（会在 validate 时报错）
                return match.group(0)
            
            return str(variables[var_name])
        
        return self.variable_pattern.sub(replace_required, text)
    
    def validate(self, prompt: str, variables: Dict[str, Any], 
                 required_vars: Optional[List[str]] = None) -> List[ValidationError]:
        """
        验证模板
        
        Args:
            prompt: 模板字符串
            variables: 提供的变量
            required_vars: 必需变量列表（从 prompt 定义中获取）
            
        Returns:
            验证错误列表
        """
        errors = []
        
        # 提取模板中的所有变量
        template_vars = set(self.extract_variables(prompt))
        
        # 检查必需变量
        if required_vars:
            for var in required_vars:
                if var not in variables:
                    errors.append(ValidationError(
                        variable=var,
                        message=f"缺少必需变量：{var}"
                    ))
        
        # 检查未使用的变量
        unused_vars = set(variables.keys()) - template_vars
        for var in unused_vars:
            errors.append(ValidationError(
                variable=var,
                message=f"未使用的变量：{var}"
            ))
        
        return errors
    
    def extract_variables(self, prompt: str) -> List[str]:
        """
        从模板中提取变量名
        
        Args:
            prompt: 模板字符串
            
        Returns:
            变量名列表
        """
        # 提取 {{variable}} 和 {{variable|default}} 形式的变量
        vars_set = set()
        
        # 标准变量
        for match in self.variable_pattern.finditer(prompt):
            vars_set.add(match.group(1))
        
        # 可选变量
        for match in self.optional_pattern.finditer(prompt):
            vars_set.add(match.group(1))
        
        # 条件变量
        for match in self.if_pattern.finditer(prompt):
            vars_set.add(match.group(1))
        
        return list(vars_set)


# 使用示例
if __name__ == "__main__":
    engine = TemplateEngine()
    
    # 示例 1：基础变量替换
    prompt1 = "你好，{{name}}！欢迎来到{{company}}。"
    result1 = engine.render(prompt1, {"name": "张三", "company": "ABC 公司"})
    print(f"示例 1: {result1}")
    
    # 示例 2：带默认值
    prompt2 = "你好，{{name|访客}}！"
    result2 = engine.render(prompt2, {})
    print(f"示例 2: {result2}")
    
    # 示例 3：条件逻辑
    prompt3 = """
    你好，{% if name %}{{name}}{% endif %}{% if not name %}访客{% endif %}！
    欢迎来到{{company}}。
    """
    result3 = engine.render(prompt3, {"name": "李四", "company": "XYZ 公司"})
    print(f"示例 3: {result3}")
    
    # 示例 4：提取变量
    prompt4 = "{{question}}关于{{topic|通用知识}}"
    vars4 = engine.extract_variables(prompt4)
    print(f"提取变量：{vars4}")
