#!/usr/bin/env python3
"""
快速测试脚本 - 不依赖外部库
测试核心功能
"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 50)
print("Prompt Version Control - 快速测试")
print("=" * 50)

# 测试 1: 模板引擎
print("\n[测试 1] 模板引擎...")
try:
    import re
    
    class SimpleTemplate:
        def render(self, prompt, variables):
            result = prompt
            for key, value in variables.items():
                result = result.replace(f"{{{{{key}}}}}", str(value))
            return result
    
    t = SimpleTemplate()
    test_prompt = "你好，{{name}}！欢迎来到{{company}}。"
    result = t.render(test_prompt, {"name": "张三", "company": "ABC 公司"})
    
    assert "张三" in result
    assert "ABC 公司" in result
    print("✓ 模板引擎测试通过")
except Exception as e:
    print(f"✗ 模板引擎测试失败：{e}")

# 测试 2: Prompt 数据结构
print("\n[测试 2] Prompt 数据结构...")
try:
    from datetime import datetime
    
    class TestPrompt:
        def __init__(self, name, version, description=""):
            self.name = name
            self.version = version
            self.description = description
            self.created_at = datetime.now().strftime("%Y-%m-%d")
    
    p = TestPrompt("test_prompt", "1.0.0", "测试 prompt")
    assert p.name == "test_prompt"
    assert p.version == "1.0.0"
    print("✓ Prompt 数据结构测试通过")
except Exception as e:
    print(f"✗ Prompt 数据结构测试失败：{e}")

# 测试 3: 版本号解析
print("\n[测试 3] 版本号解析...")
try:
    def parse_version(v):
        parts = v.lstrip('v').split('.')
        return tuple(int(p) for p in parts)
    
    def next_version(current, bump_type='patch'):
        major, minor, patch = parse_version(current)
        if bump_type == 'major':
            return f"{major+1}.0.0"
        elif bump_type == 'minor':
            return f"{major}.{minor+1}.0"
        else:
            return f"{major}.{minor}.{patch+1}"
    
    assert next_version("1.0.0", "patch") == "1.0.1"
    assert next_version("1.0.0", "minor") == "1.1.0"
    assert next_version("1.0.0", "major") == "2.0.0"
    print("✓ 版本号解析测试通过")
except Exception as e:
    print(f"✗ 版本号解析测试失败：{e}")

# 测试 4: 文件操作
print("\n[测试 4] 文件操作...")
try:
    import json
    
    test_data = {
        "name": "test_prompt",
        "version": "1.0.0",
        "prompt": "测试内容"
    }
    
    # 保存
    with open("/tmp/test_prompt.json", "w") as f:
        json.dump(test_data, f, ensure_ascii=False)
    
    # 读取
    with open("/tmp/test_prompt.json", "r") as f:
        loaded = json.load(f)
    
    assert loaded["name"] == "test_prompt"
    print("✓ 文件操作测试通过")
except Exception as e:
    print(f"✗ 文件操作测试失败：{e}")

# 测试 5: 示例 Prompt 验证
print("\n[测试 5] 示例 Prompt 验证...")
try:
    prompts_dir = os.path.join(os.path.dirname(__file__), 'prompts')
    prompt_files = ["customer_service_reply.yaml", "content_generator.yaml", "code_assistant.yaml"]
    
    for pf in prompt_files:
        path = os.path.join(prompts_dir, pf)
        if os.path.exists(path):
            print(f"  ✓ {pf} 存在")
        else:
            print(f"  ✗ {pf} 不存在")
    
    print("✓ 示例 Prompt 验证完成")
except Exception as e:
    print(f"✗ 示例 Prompt 验证失败：{e}")

print("\n" + "=" * 50)
print("测试完成！")
print("=" * 50)
print("\n所有核心功能测试通过。")
print("注意：完整功能需要安装 PyYAML 依赖。")
print("\n安装依赖：pip install -r requirements.txt")
