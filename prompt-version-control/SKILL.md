# Prompt Version Control Skill

**版本**: 1.0.0  
**作者**: dm-worker  
**创建时间**: 2026-04-15

---

## 📋 Skill 简介

**Prompt Version Control** 是一个用于管理 LLM 提示词（Prompt）版本、测试、对比和迭代的工具。

在 AI 时代，提示词成为企业重要的数据资产。本 Skill 帮助团队：
- **版本管理** — 记录每次修改，支持回滚到历史版本
- **测试对比** — 对比不同版本的输出效果
- **协作共享** — 团队共享和复用优质 prompt
- **效果评估** — 量化评估 prompt 质量

---

## 🎯 核心功能

### 1. Prompt 存储
- ✅ 支持 YAML/JSON 格式存储
- ✅ 包含完整元数据（名称、描述、作者、标签、创建时间等）
- ✅ 支持变量定义和测试用例
- ✅ 支持分类和标签管理

### 2. 版本控制
- ✅ 自动版本号（语义化版本：v1.0.0, v1.1.0, v2.0.0）
- ✅ 版本变更日志（changelog）
- ✅ 支持回滚到历史版本
- ✅ 支持版本对比（diff）

### 3. Prompt 测试
- ✅ 支持批量测试用例
- ✅ 记录每次测试的输入、输出、时间
- ✅ 支持人工评分或自动评分
- ✅ 生成测试报告

### 4. 效果对比
- ✅ 对比不同版本的输出差异
- ✅ 对比不同模型的输出差异
- ✅ 可视化展示（表格、图表）

### 5. 模板引擎
- ✅ 支持变量替换（`{{variable_name}}`）
- ✅ 支持条件逻辑（`{% if variable %}...{% endif %}`）
- ✅ 支持默认值（`{{variable|default_value}}`）

### 6. 导入导出
- ✅ 支持导出为 ZIP 包
- ✅ 支持从 ZIP 包导入
- ✅ 支持分享和复用

---

## 🚀 快速开始

### 安装依赖

```bash
cd prompt-version-control
pip install -r requirements.txt
```

### 基本使用

#### 1. 加载 Prompt

```python
from src.prompt_manager import PromptManager

manager = PromptManager("./prompts")

# 加载现有 prompt
prompt = manager.load_prompt("./prompts/customer_service_reply.yaml")
print(f"加载 Prompt: {prompt.name} v{prompt.version}")
```

#### 2. 创建新版本

```python
from src.version_control import VersionControl

vc = VersionControl("./prompts")

# 创建新版本
new_version = vc.create_version(
    prompt,
    change_message="优化回复结构，增加示例",
    bump_type='minor'  # 'major', 'minor', 'patch'
)
print(f"创建新版本：v{new_version}")
```

#### 3. 查看版本历史

```python
# 列出所有版本
versions = vc.list_versions("customer_service_reply")
for v in versions:
    print(f"v{v.version} - {v.date} - {v.changes}")
```

#### 4. 版本对比

```python
# 对比两个版本
diff = vc.diff_versions("customer_service_reply", "1.0.0", "1.1.0")
print(f"差异摘要：{diff.summary}")
for change in diff.changes:
    print(f"  {change['type']}: {change.get('content', '')[:50]}...")
```

#### 5. 运行测试

```python
from src.tester import PromptTester

tester = PromptTester()

# 运行所有测试用例
report = tester.run_all_tests(prompt)

# 打印摘要
print(tester.generate_summary(report))
```

#### 6. 版本回滚

```python
# 回滚到指定版本
new_version = vc.rollback(
    "customer_service_reply",
    target_version="1.0.0",
    message="回滚到初始版本"
)
print(f"回滚后新版本：v{new_version}")
```

---

## 📁 目录结构

```
prompt-version-control/
├── SKILL.md                 # 本文件
├── README.md                # 详细使用指南
├── requirements.txt         # Python 依赖
├── src/
│   ├── __init__.py
│   ├── prompt_manager.py    # Prompt 管理核心
│   ├── version_control.py   # 版本控制逻辑
│   ├── tester.py            # 测试框架
│   ├── comparator.py        # 对比工具
│   └── templates.py         # 模板引擎
├── prompts/                 # Prompt 存储目录
│   ├── customer_service_reply.yaml
│   ├── content_generator.yaml
│   ├── code_assistant.yaml
│   └── .versions/           # 版本历史
├── tests/                   # 测试用例
│   └── test_examples.yaml
└── scripts/
    └── export_zip.py        # 导出 ZIP 脚本
```

---

## 📝 Prompt 文件格式

```yaml
name: customer_service_reply      # Prompt 名称（唯一标识）
version: 1.0.0                     # 版本号
description: 客服回复生成 prompt    # 描述
author: dm-worker                  # 作者
tags:                              # 标签
  - customer-service
  - reply
created_at: '2026-04-15'          # 创建时间
updated_at: '2026-04-15'          # 更新时间

variables:                         # 变量定义
  - name: customer_question
    description: 客户问题
    required: true
  - name: product_name
    description: 产品名称
    required: false
    default: 我们的产品

prompt: |                          # Prompt 文本
  你是一名专业的客服代表。
  客户问题：{{customer_question}}
  产品：{{product_name|默认产品}}
  
  {% if customer_question contains "价格" %}
  注意：这是一个价格咨询问题。
  {% endif %}
  
  请提供专业、友好的回复。

test_cases:                        # 测试用例
  - name: 价格咨询
    variables:
      customer_question: 这个产品多少钱？
      product_name: 智能手表
    expected_output: 应该包含价格信息
    notes: 测试价格类问题

changelog:                         # 版本变更日志
  - version: 1.0.0
    date: '2026-04-15'
    changes:
      - 初始版本
      - 支持基础变量替换
```

---

## 🔧 API 参考

### PromptManager

```python
class PromptManager:
    def load_prompt(path: str) -> Prompt
    def save_prompt(prompt: Prompt, path: str) -> str
    def list_prompts(directory: str = None) -> List[Prompt]
    def search_prompts(query: str = "", tags: List[str] = None) -> List[Prompt]
    def create_prompt(name: str, prompt_text: str, ...) -> Prompt
    def update_prompt(prompt: Prompt, changes: Dict) -> Prompt
```

### VersionControl

```python
class VersionControl:
    def create_version(prompt: Prompt, change_message: str, bump_type: str) -> str
    def get_version(prompt_name: str, version: str) -> Prompt
    def list_versions(prompt_name: str) -> List[VersionInfo]
    def rollback(prompt_name: str, target_version: str, message: str) -> str
    def diff_versions(prompt_name: str, v1: str, v2: str) -> DiffResult
```

### PromptTester

```python
class PromptTester:
    def run_test(prompt: Prompt, test_case: TestCase) -> TestResult
    def run_all_tests(prompt: Prompt) -> TestReport
    def compare_versions(prompt_path: str, v1: str, v2: str) -> Dict
    def export_report(report: TestReport, path: str) -> str
```

### Comparator

```python
class Comparator:
    def compare_versions(results_v1: List, results_v2: List) -> ComparisonReport
    def compare_models(prompt: str, test_cases: List, outputs: Dict) -> ComparisonReport
    def export_report(report: ComparisonReport, path: str, format: str) -> str
```

### TemplateEngine

```python
class TemplateEngine:
    def render(prompt: str, variables: Dict) -> str
    def validate(prompt: str, variables: Dict, required_vars: List) -> List[ValidationError]
    def extract_variables(prompt: str) -> List[str]
```

---

## 💡 使用场景

### 场景 1：团队协作优化 Prompt

```
1. 张三查看当前版本：vc.list_versions("customer_service")
2. 张三创建新版本：vc.create_version(prompt, "优化语气")
3. 李四测试效果：tester.run_all_tests(prompt)
4. 效果不佳，回滚：vc.rollback("customer_service", "1.0.0")
5. 王五重新优化：vc.create_version(prompt, "重新优化")
```

### 场景 2：A/B 测试

```
1. 基于 v1.0.0 创建分支 v1.1.0-A 和 v1.1.0-B
2. 两个版本同时运行测试
3. 对比效果：comparator.compare_versions(...)
4. 选择优胜版本作为主版本
```

### 场景 3：模型迁移

```
1. 创建 v2.0.0，适配新模型（如从 GPT-4 迁移到 Claude 3）
2. 保留 v1.x 版本（旧模型仍可使用）
3. 测试 v2.0.0 效果
4. 效果确认后，标记 v1.x 为 deprecated
```

---

## 📦 打包发布

```bash
# 导出 ZIP 包
python scripts/export_zip.py 1.0.0

# 输出：prompt-version-control-v1.0.0.zip
```

---

## 🧪 测试

```bash
# 运行测试
python -m pytest tests/

# 或手动测试
python tests/run_tests.py
```

---

## 📚 示例 Prompt

本 Skill 包含 3 个示例 Prompt：

1. **customer_service_reply.yaml** - 客服回复生成
   - 支持变量替换
   - 包含 4 个测试用例
   - 定义回复结构

2. **content_generator.yaml** - 内容生成
   - 支持条件逻辑
   - 根据受众和长度调整
   - 包含 3 个测试用例

3. **code_assistant.yaml** - 代码助手
   - 支持多种任务类型
   - 条件逻辑处理
   - 包含 3 个测试用例

---

## 🔮 未来规划

### 第一阶段（已完成）✅
- 基础版本管理
- 模板引擎
- 测试框架

### 第二阶段（规划中）
- Web 界面
- 数据库存储
- 分支管理

### 第三阶段（规划中）
- LLM API 集成
- 自动化测试
- 效果追踪仪表板

---

## 📞 支持

如有问题或建议，请联系：
- 作者：dm-worker
- 邮箱：qijiangaoxueyi@163.com

---

*最后更新：2026-04-15*  
*版本：1.0.0*
