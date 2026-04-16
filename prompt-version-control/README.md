# Prompt Version Control

**提示词版本管理工具** — 管理 LLM 提示词的版本、测试、对比和迭代

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://example.com)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://example.com)

---

## 🎯 为什么需要 Prompt 版本管理？

在 AI 时代，提示词（Prompt）成为企业重要的数据资产：

- 💡 **提示词凝聚了领域专家的知识和经验**
- 💡 **提示词决定了 AI 输出的质量和稳定性**
- 💡 **提示词可复用、可迭代、可版本化**

但当前大多数团队的提示词管理现状：
- ❌ 散落在各处（代码、文档、聊天记录）
- ❌ 无版本控制（不知道谁改了什么）
- ❌ 无法回滚（改坏了无法恢复）
- ❌ 难以对比（哪个版本更好？）
- ❌ 缺少测试（效果如何评估？）

**Prompt Version Control** 就是为了解决这些问题而生！

---

## ✨ 特性

- 📦 **版本管理** — 自动版本号、变更日志、历史追溯
- 🔄 **回滚能力** — 随时回滚到任意历史版本
- 📊 **版本对比** — 清晰展示两个版本的差异
- 🧪 **测试框架** — 批量测试用例、评分、报告
- 📈 **效果对比** — 不同版本/模型的输出对比
- 🏷️ **模板引擎** — 变量替换、条件逻辑
- 📤 **导入导出** — ZIP 包打包、分享复用

---

## 🚀 快速开始

### 1. 安装

```bash
# 克隆或下载 Skill
cd prompt-version-control

# 安装依赖
pip install -r requirements.txt
```

### 2. 使用示例

#### 加载 Prompt

```python
from src.prompt_manager import PromptManager

manager = PromptManager("./prompts")
prompt = manager.load_prompt("./prompts/customer_service_reply.yaml")

print(f"Prompt: {prompt.name}")
print(f"版本：v{prompt.version}")
print(f"描述：{prompt.description}")
```

#### 创建新版本

```python
from src.version_control import VersionControl

vc = VersionControl("./prompts")

# 修改 prompt 内容
prompt.prompt = "你是一名专业的客服代表...\n（优化后的内容）"

# 创建新版本
new_version = vc.create_version(
    prompt,
    change_message="优化回复结构，增加示例",
    bump_type='minor'  # major/minor/patch
)

print(f"新版本：v{new_version}")
```

#### 查看版本历史

```python
versions = vc.list_versions("customer_service_reply")

for v in versions:
    print(f"v{v.version} | {v.date} | {v.changes}")
```

#### 版本对比

```python
diff = vc.diff_versions("customer_service_reply", "1.0.0", "1.1.0")

print(f"差异：{diff.summary}")
for change in diff.changes:
    print(f"  {change['type']}: {change.get('content', '')[:50]}...")
```

#### 运行测试

```python
from src.tester import PromptTester

tester = PromptTester()
report = tester.run_all_tests(prompt)

# 打印摘要
print(tester.generate_summary(report))

# 导出报告
tester.export_report(report, "./test_report.yaml")
```

#### 回滚版本

```python
# 回滚到 v1.0.0
new_version = vc.rollback(
    "customer_service_reply",
    target_version="1.0.0",
    message="v1.1.0 效果不佳，回滚"
)

print(f"回滚后新版本：v{new_version}")
```

---

## 📁 目录结构

```
prompt-version-control/
├── SKILL.md                 # Skill 详细说明
├── README.md                # 本文件
├── requirements.txt         # Python 依赖
├── src/                     # 源代码
│   ├── prompt_manager.py    # Prompt 管理
│   ├── version_control.py   # 版本控制
│   ├── tester.py            # 测试框架
│   ├── comparator.py        # 对比工具
│   └── templates.py         # 模板引擎
├── prompts/                 # Prompt 示例
│   ├── customer_service_reply.yaml
│   ├── content_generator.yaml
│   └── code_assistant.yaml
├── tests/                   # 测试用例
│   └── test_examples.yaml
└── scripts/
    └── export_zip.py        # 导出 ZIP
```

---

## 📝 Prompt 文件格式

完整的 YAML 格式示例：

```yaml
name: customer_service_reply      # 必填：Prompt 名称（唯一标识）
version: 1.0.0                     # 必填：版本号（语义化版本）
description: 客服回复生成 prompt    # 必填：描述
author: dm-worker                  # 必填：作者
tags:                              # 可选：标签列表
  - customer-service
  - reply
  - chatbot
created_at: '2026-04-15'          # 自动：创建时间
updated_at: '2026-04-15'          # 自动：更新时间

variables:                         # 可选：变量定义
  - name: customer_question
    description: 客户问题
    required: true
  - name: product_name
    description: 产品名称
    required: false
    default: 我们的产品

prompt: |                          # 必填：Prompt 文本
  你是一名专业的客服代表。
  客户问题：{{customer_question}}
  产品：{{product_name|默认产品}}
  
  {% if customer_question contains "价格" %}
  注意：这是价格咨询。
  {% endif %}
  
  请提供专业回复。

test_cases:                        # 可选：测试用例
  - name: 价格咨询
    variables:
      customer_question: 多少钱？
      product_name: 智能手表
    expected_output: 应该包含价格信息
    notes: 测试价格类问题

changelog:                         # 自动：版本变更日志
  - version: 1.0.0
    date: '2026-04-15'
    changes:
      - 初始版本
```

---

## 🔧 命令行工具（规划中）

```bash
# 创建 prompt
pvc create --name my_prompt --file prompt.yaml

# 创建版本
pvc version create --id my_prompt --message "优化内容"

# 查看历史
pvc version history --id my_prompt

# 对比版本
pvc version diff --id my_prompt --from 1.0.0 --to 1.1.0

# 回滚
pvc version rollback --id my_prompt --to 1.0.0

# 运行测试
pvc test run --file prompt.yaml

# 导出
pvc export --id my_prompt --output my_prompt.zip
```

---

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python tests/test_template.py

# 手动测试
python -c "from src.prompt_manager import PromptManager; m = PromptManager(); print('OK')"
```

---

## 📦 打包发布

```bash
# 导出 ZIP 包
python scripts/export_zip.py 1.0.0

# 输出：prompt-version-control-v1.0.0.zip
```

---

## 💡 使用场景

### 场景 1：团队协作

```
问题：多人修改同一个 prompt，不知道谁改了什么

解决：
1. 每次修改创建新版本
2. 记录变更说明
3. 随时查看历史
4. 改错了可以回滚
```

### 场景 2：A/B 测试

```
问题：两个版本的 prompt，不知道哪个更好

解决：
1. 运行相同测试用例
2. 对比测试分数
3. 选择优胜版本
```

### 场景 3：模型迁移

```
问题：从 GPT-4 迁移到 Claude 3，prompt 需要调整

解决：
1. 创建 v2.0.0 适配新模型
2. 保留 v1.x（旧模型可用）
3. 对比两个版本效果
```

---

## 🔮 路线图

### v1.0.0（当前版本）✅
- [x] 基础版本管理
- [x] 模板引擎
- [x] 测试框架
- [x] 版本对比
- [x] 示例 Prompt

### v1.1.0（规划中）
- [ ] 命令行工具
- [ ] Web 界面（基础版）
- [ ] 数据库存储支持

### v2.0.0（规划中）
- [ ] LLM API 集成
- [ ] 自动化测试
- [ ] 效果追踪仪表板
- [ ] 分支管理

---

## 📚 相关资源

- [SKILL.md](./SKILL.md) - Skill 详细说明
- [示例 Prompt](./prompts/) - 3 个示例 Prompt
- [测试用例](./tests/) - 测试示例

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 📞 联系

- 作者：dm-worker
- 邮箱：qijiangaoxueyi@163.com
- 创建时间：2026-04-15

---

**Happy Prompting! 🚀**
