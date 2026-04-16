"""
版本控制模块
负责 Prompt 版本管理、diff 对比、回滚等功能
"""

import os
import yaml
import shutil
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from pathlib import Path
from dataclasses import dataclass

import diff_match_patch as dmp

from .prompt_manager import Prompt, PromptManager


@dataclass
class VersionInfo:
    """版本信息"""
    version: str
    date: str
    author: str
    changes: List[str]
    file_size: int


@dataclass
class DiffResult:
    """Diff 结果"""
    version_from: str
    version_to: str
    changes: List[Dict]
    summary: str


class VersionControl:
    """Prompt 版本控制器"""
    
    def __init__(self, base_dir: str = "./prompts"):
        """
        初始化版本控制器
        
        Args:
            base_dir: Prompt 存储基础目录
        """
        self.base_dir = Path(base_dir)
        self.versions_dir = self.base_dir / ".versions"
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.manager = PromptManager(base_dir)
    
    def _get_versions_dir(self, prompt_name: str) -> Path:
        """获取指定 Prompt 的版本目录"""
        versions_dir = self.versions_dir / prompt_name
        versions_dir.mkdir(parents=True, exist_ok=True)
        return versions_dir
    
    def _parse_version(self, version_str: str) -> Tuple[int, int, int]:
        """解析版本号"""
        parts = version_str.lstrip('v').split('.')
        return (
            int(parts[0]) if len(parts) > 0 else 0,
            int(parts[1]) if len(parts) > 1 else 0,
            int(parts[2]) if len(parts) > 2 else 0
        )
    
    def _next_version(self, current_version: str, 
                     bump_type: str = 'patch') -> str:
        """
        计算下一个版本号
        
        Args:
            current_version: 当前版本号
            bump_type: 版本递增类型 (major/minor/patch)
            
        Returns:
            下一个版本号
        """
        major, minor, patch = self._parse_version(current_version)
        
        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump_type == 'minor':
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        return f"{major}.{minor}.{patch}"
    
    def create_version(self, prompt: Prompt, 
                      change_message: str = "",
                      bump_type: str = 'patch') -> str:
        """
        创建新版本
        
        Args:
            prompt: Prompt 对象
            change_message: 变更说明
            bump_type: 版本递增类型
            
        Returns:
            新版本号
        """
        versions_dir = self._get_versions_dir(prompt.name)
        
        # 获取当前最新版本
        latest_version = self._get_latest_version(prompt.name)
        
        if latest_version:
            # 递增版本号
            new_version = self._next_version(latest_version, bump_type)
        else:
            new_version = "1.0.0"
        
        # 更新 Prompt 版本
        prompt.version = new_version
        prompt.updated_at = datetime.now().strftime("%Y-%m-%d")
        
        # 添加 changelog
        if change_message:
            prompt.changelog.append({
                "version": new_version,
                "date": prompt.updated_at,
                "changes": [change_message]
            })
        
        # 保存版本文件
        version_file = versions_dir / f"v{new_version}.yaml"
        self.manager.save_prompt(prompt, str(version_file))
        
        # 更新主文件
        main_file = self.base_dir / f"{prompt.name}.yaml"
        self.manager.save_prompt(prompt, str(main_file))
        
        return new_version
    
    def _get_latest_version(self, prompt_name: str) -> Optional[str]:
        """获取最新版本号"""
        versions_dir = self._get_versions_dir(prompt_name)
        
        version_files = list(versions_dir.glob("v*.yaml"))
        if not version_files:
            return None
        
        # 按版本号排序
        versions = []
        for f in version_files:
            version = f.stem.lstrip('v')
            versions.append((self._parse_version(version), version))
        
        versions.sort(reverse=True)
        return versions[0][1] if versions else None
    
    def get_version(self, prompt_name: str, version: str) -> Optional[Prompt]:
        """
        获取指定版本
        
        Args:
            prompt_name: Prompt 名称
            version: 版本号
            
        Returns:
            Prompt 对象，不存在返回 None
        """
        versions_dir = self._get_versions_dir(prompt_name)
        version_file = versions_dir / f"v{version}.yaml"
        
        if not version_file.exists():
            return None
        
        return self.manager.load_prompt(str(version_file))
    
    def list_versions(self, prompt_name: str) -> List[VersionInfo]:
        """
        列出所有版本
        
        Args:
            prompt_name: Prompt 名称
            
        Returns:
            版本信息列表
        """
        versions_dir = self._get_versions_dir(prompt_name)
        version_files = sorted(versions_dir.glob("v*.yaml"))
        
        versions = []
        for f in version_files:
            try:
                prompt = self.manager.load_prompt(str(f))
                version = f.stem.lstrip('v')
                
                # 获取 changelog
                changes = []
                for log in prompt.changelog or []:
                    if log.get('version') == version:
                        changes = log.get('changes', [])
                        break
                
                versions.append(VersionInfo(
                    version=version,
                    date=prompt.updated_at or prompt.created_at,
                    author=prompt.author,
                    changes=changes,
                    file_size=f.stat().st_size
                ))
            except Exception as e:
                print(f"读取版本 {f} 失败：{e}")
        
        return versions
    
    def rollback(self, prompt_name: str, target_version: str,
                message: str = "") -> str:
        """
        回滚到指定版本
        
        Args:
            prompt_name: Prompt 名称
            target_version: 目标版本号
            message: 回滚说明
            
        Returns:
            新创建的版本号
        """
        # 获取目标版本
        target_prompt = self.get_version(prompt_name, target_version)
        if not target_prompt:
            raise ValueError(f"版本不存在：v{target_version}")
        
        # 创建新版本（复制目标版本内容）
        target_prompt.version = "0.0.0"  # 临时设置，create_version 会更新
        
        change_message = message or f"回滚到 v{target_version}"
        new_version = self.create_version(
            target_prompt,
            change_message=change_message,
            bump_type='minor'  # 回滚作为 minor 版本
        )
        
        return new_version
    
    def diff_versions(self, prompt_name: str, 
                     version_from: str, 
                     version_to: str) -> DiffResult:
        """
        对比两个版本的差异
        
        Args:
            prompt_name: Prompt 名称
            version_from: 起始版本
            version_to: 结束版本
            
        Returns:
            Diff 结果
        """
        # 加载两个版本
        prompt_from = self.get_version(prompt_name, version_from)
        prompt_to = self.get_version(prompt_name, version_to)
        
        if not prompt_from or not prompt_to:
            raise ValueError("版本不存在")
        
        # 使用 diff-match-patch 进行文本对比
        dmp_engine = dmp.diff_match_patch()
        
        # 对比 prompt 文本
        diffs = dmp_engine.diff_main(prompt_from.prompt, prompt_to.prompt)
        dmp_engine.diff_cleanupSemantic(diffs)
        
        # 解析差异
        changes = []
        for flag, text in diffs:
            if flag == -1:
                changes.append({"type": "deleted", "content": text})
            elif flag == 1:
                changes.append({"type": "added", "content": text})
            else:
                changes.append({"type": "unchanged", "content": text})
        
        # 生成摘要
        added_count = sum(1 for c in changes if c['type'] == 'added')
        deleted_count = sum(1 for c in changes if c['type'] == 'deleted')
        
        summary = f"+{added_count} 处增加，-{deleted_count} 处删除"
        
        # 对比其他字段
        if prompt_from.description != prompt_to.description:
            changes.append({
                "type": "modified",
                "field": "description",
                "old": prompt_from.description,
                "new": prompt_to.description
            })
        
        if prompt_from.tags != prompt_to.tags:
            changes.append({
                "type": "modified",
                "field": "tags",
                "old": prompt_from.tags,
                "new": prompt_to.tags
            })
        
        return DiffResult(
            version_from=version_from,
            version_to=version_to,
            changes=changes,
            summary=summary
        )
    
    def export_version(self, prompt_name: str, version: str,
                      output_path: str) -> str:
        """
        导出指定版本
        
        Args:
            prompt_name: Prompt 名称
            version: 版本号
            output_path: 输出路径
            
        Returns:
            导出文件路径
        """
        prompt = self.get_version(prompt_name, version)
        if not prompt:
            raise ValueError(f"版本不存在：v{version}")
        
        return self.manager.save_prompt(prompt, output_path)


# 使用示例
if __name__ == "__main__":
    vc = VersionControl("./test_prompts")
    
    # 创建测试 Prompt
    from prompt_manager import PromptManager
    manager = PromptManager("./test_prompts")
    
    prompt = manager.create_prompt(
        name="test_prompt",
        prompt_text="你好，{{name}}！",
        description="测试 prompt",
        author="tester"
    )
    
    # 创建版本
    v1 = vc.create_version(prompt, "初始版本")
    print(f"创建版本：v{v1}")
    
    # 更新
    prompt.prompt = "你好，{{name}}！欢迎到来。"
    v2 = vc.create_version(prompt, "增加欢迎语", bump_type='minor')
    print(f"创建版本：v{v2}")
    
    # 列出版本
    versions = vc.list_versions("test_prompt")
    print(f"版本列表：{[v.version for v in versions]}")
    
    # 对比版本
    diff = vc.diff_versions("test_prompt", "1.0.0", "1.1.0")
    print(f"版本差异：{diff.summary}")
    
    # 回滚
    new_v = vc.rollback("test_prompt", "1.0.0", "回滚测试")
    print(f"回滚后新版本：v{new_v}")
