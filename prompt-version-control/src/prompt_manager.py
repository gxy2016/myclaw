"""
Prompt 管理模块
负责 Prompt 的加载、保存、搜索等操作
"""

import os
import yaml
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class PromptVariable:
    """Prompt 变量定义"""
    name: str
    description: str = ""
    required: bool = True
    default: Optional[str] = None


@dataclass
class TestCase:
    """测试用例"""
    name: str
    variables: Dict[str, str]
    expected_output: str = ""
    actual_output: Optional[str] = None
    score: Optional[float] = None
    notes: str = ""


@dataclass
class Prompt:
    """Prompt 数据结构"""
    name: str
    version: str
    description: str = ""
    author: str = ""
    tags: List[str] = None
    created_at: str = ""
    updated_at: str = ""
    variables: List[PromptVariable] = None
    prompt: str = ""
    test_cases: List[TestCase] = None
    changelog: List[Dict] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.variables is None:
            self.variables = []
        if self.test_cases is None:
            self.test_cases = []
        if self.changelog is None:
            self.changelog = []
        if self.metadata is None:
            self.metadata = {}
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d")
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Prompt':
        """从字典创建"""
        # 转换 variables
        variables = []
        for v in data.get('variables', []):
            if isinstance(v, dict):
                variables.append(PromptVariable(**v))
            else:
                variables.append(v)
        data['variables'] = variables
        
        # 转换 test_cases
        test_cases = []
        for t in data.get('test_cases', []):
            if isinstance(t, dict):
                test_cases.append(TestCase(**t))
            else:
                test_cases.append(t)
        data['test_cases'] = test_cases
        
        return cls(**data)


class PromptManager:
    """Prompt 管理器"""
    
    def __init__(self, base_dir: str = "./prompts"):
        """
        初始化 Prompt 管理器
        
        Args:
            base_dir: Prompt 存储基础目录
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def load_prompt(self, path: str) -> Prompt:
        """
        加载 Prompt
        
        Args:
            path: 文件路径（.yaml 或 .json）
            
        Returns:
            Prompt 对象
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Prompt 文件不存在：{path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"不支持的文件格式：{path.suffix}")
        
        return Prompt.from_dict(data)
    
    def save_prompt(self, prompt: Prompt, path: str) -> str:
        """
        保存 Prompt
        
        Args:
            prompt: Prompt 对象
            path: 保存路径
            
        Returns:
            保存的路径
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = prompt.to_dict()
        
        with open(path, 'w', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
            elif path.suffix == '.json':
                json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                # 默认保存为 YAML
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        
        return str(path)
    
    def list_prompts(self, directory: Optional[str] = None) -> List[Prompt]:
        """
        列出目录中的所有 Prompt
        
        Args:
            directory: 目录路径，默认为 base_dir
            
        Returns:
            Prompt 列表
        """
        if directory is None:
            directory = self.base_dir
        
        prompts = []
        dir_path = Path(directory)
        
        for file in dir_path.glob("*.yaml"):
            if '.versions' in str(file):
                continue  # 跳过版本目录
            try:
                prompt = self.load_prompt(str(file))
                prompts.append(prompt)
            except Exception as e:
                print(f"加载 {file} 失败：{e}")
        
        for file in dir_path.glob("*.yml"):
            if '.versions' in str(file):
                continue
            try:
                prompt = self.load_prompt(str(file))
                prompts.append(prompt)
            except Exception as e:
                print(f"加载 {file} 失败：{e}")
        
        return prompts
    
    def search_prompts(self, query: str = "", tags: Optional[List[str]] = None,
                      directory: Optional[str] = None) -> List[Prompt]:
        """
        搜索 Prompt
        
        Args:
            query: 搜索关键词（名称、描述）
            tags: 标签过滤
            directory: 搜索目录
            
        Returns:
            匹配的 Prompt 列表
        """
        prompts = self.list_prompts(directory)
        results = []
        
        for prompt in prompts:
            # 关键词匹配
            if query:
                query_lower = query.lower()
                if query_lower not in prompt.name.lower() and \
                   query_lower not in prompt.description.lower():
                    continue
            
            # 标签匹配
            if tags:
                if not any(tag in prompt.tags for tag in tags):
                    continue
            
            results.append(prompt)
        
        return results
    
    def create_prompt(self, name: str, prompt_text: str, 
                     description: str = "", author: str = "",
                     tags: Optional[List[str]] = None,
                     variables: Optional[List[Dict]] = None) -> Prompt:
        """
        创建新 Prompt
        
        Args:
            name: Prompt 名称
            prompt_text: Prompt 文本
            description: 描述
            author: 作者
            tags: 标签列表
            variables: 变量定义列表
            
        Returns:
            创建的 Prompt 对象
        """
        prompt = Prompt(
            name=name,
            version="1.0.0",
            description=description,
            author=author,
            tags=tags or [],
            variables=[PromptVariable(**v) for v in variables] if variables else [],
            prompt=prompt_text,
            changelog=[{
                "version": "1.0.0",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "changes": ["初始版本"]
            }]
        )
        
        return prompt
    
    def update_prompt(self, prompt: Prompt, changes: Dict[str, Any],
                     change_message: str = "") -> Prompt:
        """
        更新 Prompt
        
        Args:
            prompt: 原 Prompt
            changes: 变更内容
            change_message: 变更说明
            
        Returns:
            更新后的 Prompt
        """
        # 更新字段
        for key, value in changes.items():
            if hasattr(prompt, key):
                setattr(prompt, key, value)
        
        # 更新版本号和更新时间
        prompt.updated_at = datetime.now().strftime("%Y-%m-%d")
        
        # 添加 changelog
        if change_message:
            prompt.changelog.append({
                "version": prompt.version,
                "date": prompt.updated_at,
                "changes": [change_message]
            })
        
        return prompt


# 使用示例
if __name__ == "__main__":
    manager = PromptManager("./test_prompts")
    
    # 创建示例 Prompt
    prompt = manager.create_prompt(
        name="customer_service_reply",
        prompt_text="你是一名专业的客服代表。客户问题：{{question}}",
        description="客服回复生成 prompt",
        author="dm-worker",
        tags=["customer-service", "reply"],
        variables=[
            {"name": "question", "description": "客户问题", "required": True}
        ]
    )
    
    # 保存
    manager.save_prompt(prompt, "./test_prompts/example.yaml")
    print(f"已保存 Prompt: {prompt.name} v{prompt.version}")
    
    # 加载
    loaded = manager.load_prompt("./test_prompts/example.yaml")
    print(f"已加载 Prompt: {loaded.name} v{loaded.version}")
    
    # 搜索
    results = manager.search_prompts(query="customer", tags=["customer-service"])
    print(f"搜索结果：{len(results)} 个")
