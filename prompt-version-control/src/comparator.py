"""
对比模块
负责不同版本/模型的输出对比
"""

import yaml
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ComparisonItem:
    """对比项"""
    input_variables: Dict[str, str]
    outputs: Dict[str, str]  # version/model -> output
    scores: Dict[str, float]


@dataclass
class ComparisonReport:
    """对比报告"""
    prompt_name: str
    comparison_type: str  # "version" or "model"
    items: List[ComparisonItem]
    statistics: Dict[str, Any]
    generated_at: str = ""
    
    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


class Comparator:
    """Prompt 对比器"""
    
    def __init__(self):
        """初始化对比器"""
        pass
    
    def compare_versions(self, test_results_v1: List[Dict],
                        test_results_v2: List[Dict]) -> ComparisonReport:
        """
        对比两个版本的测试结果
        
        Args:
            test_results_v1: 版本 1 的测试结果列表
            test_results_v2: 版本 2 的测试结果列表
            
        Returns:
            对比报告
        """
        items = []
        
        # 按测试名称匹配
        v1_by_name = {r['test_name']: r for r in test_results_v1}
        v2_by_name = {r['test_name']: r for r in test_results_v2}
        
        all_names = set(v1_by_name.keys()) | set(v2_by_name.keys())
        
        for name in all_names:
            r1 = v1_by_name.get(name, {})
            r2 = v2_by_name.get(name, {})
            
            item = ComparisonItem(
                input_variables=r1.get('input_variables', r2.get('input_variables', {})),
                outputs={
                    "v1": r1.get('actual_output', ''),
                    "v2": r2.get('actual_output', '')
                },
                scores={
                    "v1": r1.get('score', 0.0),
                    "v2": r2.get('score', 0.0)
                }
            )
            items.append(item)
        
        # 计算统计
        statistics = self._calculate_statistics(items)
        
        # 获取 prompt 名称
        prompt_name = "unknown"
        if test_results_v1:
            prompt_name = test_results_v1[0].get('prompt_name', 'unknown')
        
        report = ComparisonReport(
            prompt_name=prompt_name,
            comparison_type="version",
            items=items,
            statistics=statistics
        )
        
        return report
    
    def compare_models(self, prompt: str, test_cases: List[Dict],
                      model_outputs: Dict[str, List[Dict]]) -> ComparisonReport:
        """
        对比不同模型的输出
        
        Args:
            prompt: Prompt 文本
            test_cases: 测试用例列表
            model_outputs: 各模型的输出 {model_name: [outputs]}
            
        Returns:
            对比报告
        """
        items = []
        
        for i, test_case in enumerate(test_cases):
            outputs = {}
            scores = {}
            
            for model_name, outputs_list in model_outputs.items():
                if i < len(outputs_list):
                    outputs[model_name] = outputs_list[i].get('output', '')
                    scores[model_name] = outputs_list[i].get('score', 0.0)
            
            item = ComparisonItem(
                input_variables=test_case.get('variables', {}),
                outputs=outputs,
                scores=scores
            )
            items.append(item)
        
        # 计算统计
        statistics = self._calculate_statistics(items)
        
        report = ComparisonReport(
            prompt_name="model_comparison",
            comparison_type="model",
            items=items,
            statistics=statistics
        )
        
        return report
    
    def _calculate_statistics(self, items: List[ComparisonItem]) -> Dict[str, Any]:
        """
        计算统计信息
        
        Args:
            items: 对比项列表
            
        Returns:
            统计信息字典
        """
        if not items:
            return {}
        
        # 获取所有版本/模型名称
        all_keys = set()
        for item in items:
            all_keys.update(item.outputs.keys())
        
        statistics = {
            "total_items": len(items),
            "versions": list(all_keys),
            "average_scores": {},
            "score_improvements": {}
        }
        
        # 计算每个版本的平均分
        for key in all_keys:
            scores = [item.scores.get(key, 0.0) for item in items if key in item.scores]
            if scores:
                statistics["average_scores"][key] = sum(scores) / len(scores)
        
        # 计算改进（如果有两个版本）
        keys = list(all_keys)
        if len(keys) >= 2:
            v1, v2 = keys[0], keys[1]
            v1_avg = statistics["average_scores"].get(v1, 0.0)
            v2_avg = statistics["average_scores"].get(v2, 0.0)
            statistics["score_improvements"] = {
                "from": v1,
                "to": v2,
                "improvement": v2_avg - v1_avg,
                "improvement_percent": ((v2_avg - v1_avg) / v1_avg * 100) if v1_avg > 0 else 0
            }
        
        return statistics
    
    def export_report(self, report: ComparisonReport, 
                     output_path: str, format: str = "yaml") -> str:
        """
        导出对比报告
        
        Args:
            report: 对比报告
            output_path: 输出路径
            format: 导出格式 (yaml/json/markdown)
            
        Returns:
            导出文件路径
        """
        path = Path(output_path)
        
        if format == "yaml":
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(report.to_dict(), f, allow_unicode=True, default_flow_style=False)
        
        elif format == "json":
            import json
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        
        elif format == "markdown":
            md_content = self._report_to_markdown(report)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(md_content)
        
        return str(path)
    
    def _report_to_markdown(self, report: ComparisonReport) -> str:
        """
        将对比报告转换为 Markdown
        
        Args:
            report: 对比报告
            
        Returns:
            Markdown 文本
        """
        lines = []
        lines.append(f"# 对比报告：{report.prompt_name}")
        lines.append(f"**对比类型**: {report.comparison_type}")
        lines.append(f"**生成时间**: {report.generated_at}")
        lines.append("")
        
        # 统计信息
        lines.append("## 统计摘要")
        stats = report.statistics
        lines.append(f"- 总测试项：{stats.get('total_items', 0)}")
        lines.append(f"- 对比版本：{', '.join(stats.get('versions', []))}")
        lines.append("")
        
        # 平均分对比
        lines.append("### 平均分数")
        for version, score in stats.get('average_scores', {}).items():
            lines.append(f"- {version}: {score:.2f}")
        lines.append("")
        
        # 改进情况
        if stats.get('score_improvements'):
            imp = stats['score_improvements']
            lines.append("### 改进情况")
            lines.append(f"- 从 {imp['from']} 到 {imp['to']}")
            lines.append(f"- 绝对改进：{imp['improvement']:.2f}")
            lines.append(f"- 百分比改进：{imp['improvement_percent']:.1f}%")
            lines.append("")
        
        # 详细对比
        lines.append("## 详细对比")
        for i, item in enumerate(items, 1):
            lines.append(f"### 测试 {i}")
            lines.append(f"**输入**: {item.input_variables}")
            lines.append("")
            
            for version, output in item.outputs.items():
                lines.append(f"**{version} 输出**:")
                lines.append(f"> {output}")
                lines.append("")
            
            lines.append(f"**分数**: " + ", ".join([f"{k}: {v:.2f}" for k, v in item.scores.items()]))
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_visual_comparison(self, report: ComparisonReport) -> str:
        """
        生成可视化对比表格
        
        Args:
            report: 对比报告
            
        Returns:
            表格文本
        """
        lines = []
        
        # 表头
        headers = ["测试项"]
        headers.extend(report.statistics.get('versions', []))
        headers.append("改进")
        
        # 计算列宽
        col_widths = [len(h) for h in headers]
        
        # 添加数据行
        for i, item in enumerate(report.items, 1):
            row = [f"测试 {i}"]
            for version in report.statistics.get('versions', []):
                score = item.scores.get(version, 0.0)
                row.append(f"{score:.2f}")
            
            # 计算改进
            if len(report.statistics.get('versions', [])) >= 2:
                v1, v2 = report.statistics['versions'][:2]
                diff = item.scores.get(v2, 0.0) - item.scores.get(v1, 0.0)
                row.append(f"{diff:+.2f}")
            
            # 更新列宽
            for j, cell in enumerate(row):
                col_widths[j] = max(col_widths[j], len(cell))
        
        # 生成表格
        separator = "|" + "|".join(["-" * (w + 2) for w in col_widths]) + "|"
        header_row = "|" + "|".join([h.center(w + 2) for h, w in zip(headers, col_widths)]) + "|"
        
        lines.append(separator)
        lines.append(header_row)
        lines.append(separator)
        
        for i, item in enumerate(report.items, 1):
            row = [f"测试 {i}"]
            for version in report.statistics.get('versions', []):
                score = item.scores.get(version, 0.0)
                row.append(f"{score:.2f}".center(col_widths[1] + 2))
            
            if len(report.statistics.get('versions', [])) >= 2:
                v1, v2 = report.statistics['versions'][:2]
                diff = item.scores.get(v2, 0.0) - item.scores.get(v1, 0.0)
                diff_str = f"{diff:+.2f}"
                row.append(diff_str.center(col_widths[-1] + 2))
            
            lines.append("|" + "|".join(row) + "|")
        
        lines.append(separator)
        
        return "\n".join(lines)


# 使用示例
if __name__ == "__main__":
    # 模拟测试结果
    test_results_v1 = [
        {
            "test_name": "测试 1",
            "input_variables": {"name": "张三"},
            "actual_output": "你好，张三！",
            "score": 0.85
        },
        {
            "test_name": "测试 2",
            "input_variables": {"name": "李四"},
            "actual_output": "你好，李四！",
            "score": 0.90
        }
    ]
    
    test_results_v2 = [
        {
            "test_name": "测试 1",
            "input_variables": {"name": "张三"},
            "actual_output": "你好，张三！欢迎到来。",
            "score": 0.92
        },
        {
            "test_name": "测试 2",
            "input_variables": {"name": "李四"},
            "actual_output": "你好，李四！欢迎到来。",
            "score": 0.88
        }
    ]
    
    # 对比
    comparator = Comparator()
    report = comparator.compare_versions(test_results_v1, test_results_v2)
    
    # 打印统计
    print(f"对比报告：{report.prompt_name}")
    print(f"版本：{report.statistics['versions']}")
    print(f"平均分：{report.statistics['average_scores']}")
    
    # 生成表格
    print("\n可视化对比:")
    print(comparator.generate_visual_comparison(report))
