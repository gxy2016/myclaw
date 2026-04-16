"""
测试模块
负责 Prompt 测试、评分、报告生成
"""

import yaml
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict

from .prompt_manager import Prompt, TestCase, PromptManager
from .templates import TemplateEngine


@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    input_variables: Dict[str, str]
    rendered_prompt: str
    actual_output: str = ""
    expected_output: str = ""
    score: float = 0.0
    duration_ms: float = 0.0
    timestamp: str = ""
    notes: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class TestReport:
    """测试报告"""
    prompt_name: str
    prompt_version: str
    total_tests: int
    passed_tests: int
    average_score: float
    total_duration_ms: float
    test_results: List[TestResult]
    generated_at: str = ""
    
    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


class PromptTester:
    """Prompt 测试器"""
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        初始化测试器
        
        Args:
            llm_client: LLM 客户端（可选，用于实际调用模型）
        """
        self.template_engine = TemplateEngine()
        self.llm_client = llm_client
    
    def run_test(self, prompt: Prompt, test_case: TestCase,
                auto_execute: bool = False) -> TestResult:
        """
        运行单个测试
        
        Args:
            prompt: Prompt 对象
            test_case: 测试用例
            auto_execute: 是否自动执行 LLM 调用
            
        Returns:
            测试结果
        """
        import time
        start_time = time.time()
        
        # 渲染 Prompt
        rendered = self.template_engine.render(
            prompt.prompt,
            test_case.variables
        )
        
        # 执行 LLM 调用（如果启用）
        actual_output = ""
        if auto_execute and self.llm_client:
            try:
                actual_output = self.llm_client.generate(rendered)
            except Exception as e:
                actual_output = f"Error: {str(e)}"
        
        duration_ms = (time.time() - start_time) * 1000
        
        # 创建测试结果
        result = TestResult(
            test_name=test_case.name,
            input_variables=test_case.variables,
            rendered_prompt=rendered,
            actual_output=actual_output,
            expected_output=test_case.expected_output,
            score=test_case.score or 0.0,
            duration_ms=duration_ms,
            notes=test_case.notes
        )
        
        return result
    
    def run_all_tests(self, prompt: Prompt,
                     auto_execute: bool = False) -> TestReport:
        """
        运行所有测试用例
        
        Args:
            prompt: Prompt 对象
            auto_execute: 是否自动执行 LLM 调用
            
        Returns:
            测试报告
        """
        results = []
        passed_count = 0
        total_score = 0.0
        total_duration = 0.0
        
        for test_case in prompt.test_cases:
            result = self.run_test(prompt, test_case, auto_execute)
            results.append(result)
            
            # 统计
            if result.score >= 0.8:  # 80 分以上算通过
                passed_count += 1
            total_score += result.score
            total_duration += result.duration_ms
        
        # 计算平均分
        avg_score = total_score / len(results) if results else 0.0
        
        # 创建测试报告
        report = TestReport(
            prompt_name=prompt.name,
            prompt_version=prompt.version,
            total_tests=len(results),
            passed_tests=passed_count,
            average_score=avg_score,
            total_duration_ms=total_duration,
            test_results=results
        )
        
        return report
    
    def compare_versions(self, prompt_path: str, version1: str,
                        version2: str, test_cases: List[TestCase],
                        auto_execute: bool = False) -> Dict:
        """
        对比两个版本的测试结果
        
        Args:
            prompt_path: Prompt 文件路径
            version1: 版本 1
            version2: 版本 2
            test_cases: 测试用例列表
            auto_execute: 是否自动执行
            
        Returns:
            对比报告
        """
        from .version_control import VersionControl
        
        vc = VersionControl()
        
        # 加载两个版本
        prompt1 = vc.get_version_from_path(prompt_path, version1)
        prompt2 = vc.get_version_from_path(prompt_path, version2)
        
        if not prompt1 or not prompt2:
            raise ValueError("版本加载失败")
        
        # 运行测试
        report1 = self.run_all_tests(prompt1, auto_execute)
        report2 = self.run_all_tests(prompt2, auto_execute)
        
        # 生成对比报告
        comparison = {
            "version1": {
                "version": version1,
                "average_score": report1.average_score,
                "passed_tests": report1.passed_tests,
                "total_duration_ms": report1.total_duration_ms
            },
            "version2": {
                "version": version2,
                "average_score": report2.average_score,
                "passed_tests": report2.passed_tests,
                "total_duration_ms": report2.total_duration_ms
            },
            "improvement": {
                "score_diff": report2.average_score - report1.average_score,
                "passed_diff": report2.passed_tests - report1.passed_tests,
                "duration_diff": report2.total_duration_ms - report1.total_duration_ms
            }
        }
        
        return comparison
    
    def export_report(self, report: TestReport, output_path: str) -> str:
        """
        导出测试报告
        
        Args:
            report: 测试报告
            output_path: 输出路径
            
        Returns:
            导出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(report.to_dict(), f, allow_unicode=True, default_flow_style=False)
        
        return output_path
    
    def generate_summary(self, report: TestReport) -> str:
        """
        生成测试摘要
        
        Args:
            report: 测试报告
            
        Returns:
            摘要文本
        """
        summary = []
        summary.append(f"测试报告：{report.prompt_name} v{report.prompt_version}")
        summary.append(f"生成时间：{report.generated_at}")
        summary.append("")
        summary.append("总体统计:")
        summary.append(f"  - 总测试数：{report.total_tests}")
        summary.append(f"  - 通过测试：{report.passed_tests}")
        summary.append(f"  - 平均分数：{report.average_score:.2f}")
        summary.append(f"  - 总耗时：{report.total_duration_ms:.2f}ms")
        summary.append("")
        summary.append("测试结果:")
        
        for result in report.test_results:
            status = "✓" if result.score >= 0.8 else "✗"
            summary.append(f"  {status} {result.test_name}: {result.score:.2f}")
        
        return "\n".join(summary)


# 使用示例
if __name__ == "__main__":
    from prompt_manager import PromptManager, TestCase
    
    # 创建测试 Prompt
    manager = PromptManager("./test_prompts")
    prompt = manager.create_prompt(
        name="test_prompt",
        prompt_text="你好，{{name}}！请回答：{{question}}",
        description="测试 prompt",
        author="tester",
        variables=[
            {"name": "name", "description": "姓名", "required": True},
            {"name": "question", "description": "问题", "required": True}
        ]
    )
    
    # 添加测试用例
    prompt.test_cases = [
        TestCase(
            name="基础测试",
            variables={"name": "张三", "question": "今天天气如何？"},
            expected_output="应该友好问候并回答问题",
            notes="测试基础功能"
        ),
        TestCase(
            name="边界测试",
            variables={"name": "李四", "question": ""},
            expected_output="应该处理空问题",
            notes="测试边界情况"
        )
    ]
    
    # 运行测试
    tester = PromptTester()
    report = tester.run_all_tests(prompt)
    
    # 打印摘要
    print(tester.generate_summary(report))
    
    # 导出报告
    tester.export_report(report, "./test_prompts/test_report.yaml")
    print(f"测试报告已导出")
