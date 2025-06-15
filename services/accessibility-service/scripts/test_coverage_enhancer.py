#!/usr/bin/env python3
"""
测试覆盖率提升脚本 - 自动生成测试用例并提高测试覆盖率
"""

import ast
import json
import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class CoverageReport:
    """覆盖率报告"""

    total_lines: int = 0
    covered_lines: int = 0
    coverage_percentage: float = 0.0
    uncovered_files: List[str] = None
    uncovered_functions: List[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.uncovered_files is None:
            self.uncovered_files = []
        if self.uncovered_functions is None:
            self.uncovered_functions = []


@dataclass
class TestCase:
    """测试用例"""

    function_name: str
    test_name: str
    test_code: str
    imports: List[str]
    description: str


class TestGenerator:
    """测试生成器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.test_templates = self._load_test_templates()

    def _load_test_templates(self) -> Dict[str, str]:
        """加载测试模板"""
        return {
            "simple_function": '''
async def test_{function_name}(self):
    """测试 {function_name} 函数"""
    # 准备测试数据
    {test_data}
    
    # 执行测试
    result = await {module_name}.{function_name}({parameters})
    
    # 验证结果
    assert result is not None
    {assertions}
''',
            "class_method": '''
async def test_{class_name}_{method_name}(self):
    """测试 {class_name}.{method_name} 方法"""
    # 创建实例
    instance = {class_name}({init_params})
    
    # 准备测试数据
    {test_data}
    
    # 执行测试
    result = await instance.{method_name}({parameters})
    
    # 验证结果
    assert result is not None
    {assertions}
''',
            "exception_test": '''
async def test_{function_name}_exception(self):
    """测试 {function_name} 异常处理"""
    with pytest.raises({exception_type}):
        await {module_name}.{function_name}({invalid_parameters})
''',
            "mock_test": '''
@patch('{mock_target}')
async def test_{function_name}_with_mock(self, mock_{mock_name}):
    """测试 {function_name} 使用Mock"""
    # 配置Mock
    mock_{mock_name}.return_value = {mock_return}
    
    # 执行测试
    result = await {module_name}.{function_name}({parameters})
    
    # 验证Mock调用
    mock_{mock_name}.assert_called_once_with({expected_args})
    
    # 验证结果
    assert result == {expected_result}
''',
        }

    def generate_tests_for_file(self, file_path: Path) -> List[TestCase]:
        """为文件生成测试用例"""
        logger.info(f"为文件 {file_path} 生成测试用例...")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            test_cases = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("_"):  # 跳过私有函数
                        test_case = self._generate_function_test(node, file_path)
                        if test_case:
                            test_cases.append(test_case)

                elif isinstance(node, ast.ClassDef):
                    class_tests = self._generate_class_tests(node, file_path)
                    test_cases.extend(class_tests)

            return test_cases

        except Exception as e:
            logger.error(f"生成测试用例失败 {file_path}: {e}")
            return []

    def _generate_function_test(
        self, node: ast.FunctionDef, file_path: Path
    ) -> Optional[TestCase]:
        """生成函数测试用例"""
        try:
            # 分析函数参数
            params = self._analyze_function_params(node)

            # 生成测试数据
            test_data = self._generate_test_data(params)

            # 生成测试代码
            module_name = self._get_module_name(file_path)

            test_code = self.test_templates["simple_function"].format(
                function_name=node.name,
                module_name=module_name,
                parameters=", ".join(f"{p}={v}" for p, v in test_data.items()),
                test_data=self._format_test_data(test_data),
                assertions=self._generate_assertions(node),
            )

            return TestCase(
                function_name=node.name,
                test_name=f"test_{node.name}",
                test_code=test_code,
                imports=[f"from {module_name} import {node.name}"],
                description=f"测试 {node.name} 函数的基本功能",
            )

        except Exception as e:
            logger.warning(f"生成函数测试失败 {node.name}: {e}")
            return None

    def _generate_class_tests(
        self, node: ast.ClassDef, file_path: Path
    ) -> List[TestCase]:
        """生成类测试用例"""
        test_cases = []

        try:
            for method in node.body:
                if isinstance(method, ast.FunctionDef) and not method.name.startswith(
                    "_"
                ):
                    test_case = self._generate_method_test(node.name, method, file_path)
                    if test_case:
                        test_cases.append(test_case)

        except Exception as e:
            logger.warning(f"生成类测试失败 {node.name}: {e}")

        return test_cases

    def _generate_method_test(
        self, class_name: str, method: ast.FunctionDef, file_path: Path
    ) -> Optional[TestCase]:
        """生成方法测试用例"""
        try:
            # 分析方法参数（排除self）
            params = self._analyze_function_params(method, skip_self=True)

            # 生成测试数据
            test_data = self._generate_test_data(params)

            # 生成初始化参数
            init_params = self._generate_init_params(class_name)

            # 生成测试代码
            test_code = self.test_templates["class_method"].format(
                class_name=class_name,
                method_name=method.name,
                init_params=init_params,
                parameters=", ".join(f"{p}={v}" for p, v in test_data.items()),
                test_data=self._format_test_data(test_data),
                assertions=self._generate_assertions(method),
            )

            return TestCase(
                function_name=f"{class_name}.{method.name}",
                test_name=f"test_{class_name.lower()}_{method.name}",
                test_code=test_code,
                imports=[
                    f"from {self._get_module_name(file_path)} import {class_name}"
                ],
                description=f"测试 {class_name}.{method.name} 方法的基本功能",
            )

        except Exception as e:
            logger.warning(f"生成方法测试失败 {class_name}.{method.name}: {e}")
            return None

    def _analyze_function_params(
        self, node: ast.FunctionDef, skip_self: bool = False
    ) -> List[Dict[str, Any]]:
        """分析函数参数"""
        params = []

        for arg in node.args.args:
            if skip_self and arg.arg == "self":
                continue

            param_info = {
                "name": arg.arg,
                "type": self._get_param_type(arg),
                "default": None,
            }

            params.append(param_info)

        return params

    def _get_param_type(self, arg: ast.arg) -> str:
        """获取参数类型"""
        if arg.annotation:
            if isinstance(arg.annotation, ast.Name):
                return arg.annotation.id
            elif isinstance(arg.annotation, ast.Constant):
                return str(arg.annotation.value)

        return "Any"

    def _generate_test_data(self, params: List[Dict[str, Any]]) -> Dict[str, str]:
        """生成测试数据"""
        test_data = {}

        for param in params:
            param_type = param["type"]
            param_name = param["name"]

            if param_type in ["str", "String"]:
                test_data[param_name] = f'"test_{param_name}"'
            elif param_type in ["int", "Integer"]:
                test_data[param_name] = "42"
            elif param_type in ["float", "Float"]:
                test_data[param_name] = "3.14"
            elif param_type in ["bool", "Boolean"]:
                test_data[param_name] = "True"
            elif param_type in ["list", "List"]:
                test_data[param_name] = "[]"
            elif param_type in ["dict", "Dict"]:
                test_data[param_name] = "{}"
            else:
                test_data[param_name] = "None"

        return test_data

    def _format_test_data(self, test_data: Dict[str, str]) -> str:
        """格式化测试数据"""
        if not test_data:
            return "# 无需测试数据"

        lines = []
        for name, value in test_data.items():
            lines.append(f"    {name} = {value}")

        return "\n".join(lines)

    def _generate_assertions(self, node: ast.FunctionDef) -> str:
        """生成断言"""
        assertions = []

        # 基于返回类型生成断言
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return_type = node.returns.id
                if return_type == "bool":
                    assertions.append("assert isinstance(result, bool)")
                elif return_type == "str":
                    assertions.append("assert isinstance(result, str)")
                    assertions.append("assert len(result) > 0")
                elif return_type == "int":
                    assertions.append("assert isinstance(result, int)")
                elif return_type == "list":
                    assertions.append("assert isinstance(result, list)")
                elif return_type == "dict":
                    assertions.append("assert isinstance(result, dict)")

        if not assertions:
            assertions.append("# 添加具体的断言")

        return "\n    ".join(assertions)

    def _generate_init_params(self, class_name: str) -> str:
        """生成初始化参数"""
        # 简化的初始化参数生成
        common_params = {
            "Service": "config={}",
            "Client": 'endpoint="http://localhost"',
            "Manager": "config={}",
            "Handler": "config={}",
            "Processor": "config={}",
        }

        for suffix, params in common_params.items():
            if class_name.endswith(suffix):
                return params

        return ""

    def _get_module_name(self, file_path: Path) -> str:
        """获取模块名"""
        relative_path = file_path.relative_to(self.project_root)
        module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        return ".".join(module_parts)


class CoverageAnalyzer:
    """覆盖率分析器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)

    def analyze_coverage(self) -> CoverageReport:
        """分析测试覆盖率"""
        logger.info("分析测试覆盖率...")

        try:
            # 运行coverage
            result = subprocess.run(
                ["python", "-m", "coverage", "run", "--source=.", "-m", "pytest"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode != 0:
                logger.warning(f"运行测试失败: {result.stderr}")

            # 生成覆盖率报告
            coverage_result = subprocess.run(
                ["python", "-m", "coverage", "report", "--format=json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if coverage_result.returncode == 0:
                coverage_data = json.loads(coverage_result.stdout)
                return self._parse_coverage_data(coverage_data)
            else:
                logger.warning("无法生成覆盖率报告，使用默认值")
                return CoverageReport()

        except Exception as e:
            logger.error(f"分析覆盖率失败: {e}")
            return CoverageReport()

    def _parse_coverage_data(self, coverage_data: Dict[str, Any]) -> CoverageReport:
        """解析覆盖率数据"""
        totals = coverage_data.get("totals", {})

        report = CoverageReport(
            total_lines=totals.get("num_statements", 0),
            covered_lines=totals.get("covered_lines", 0),
            coverage_percentage=totals.get("percent_covered", 0.0),
        )

        # 分析未覆盖的文件
        files = coverage_data.get("files", {})
        for file_path, file_data in files.items():
            if file_data.get("summary", {}).get("percent_covered", 0) < 80:
                report.uncovered_files.append(file_path)

        return report


class TestCoverageEnhancer:
    """测试覆盖率提升器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.test_generator = TestGenerator(project_root)
        self.coverage_analyzer = CoverageAnalyzer(project_root)

    def enhance_test_coverage(self) -> Dict[str, Any]:
        """提升测试覆盖率"""
        logger.info("开始提升测试覆盖率...")

        # 分析当前覆盖率
        initial_coverage = self.coverage_analyzer.analyze_coverage()
        logger.info(f"当前覆盖率: {initial_coverage.coverage_percentage:.1f}%")

        results = {
            "initial_coverage": initial_coverage,
            "generated_tests": [],
            "final_coverage": None,
        }

        # 为未覆盖的文件生成测试
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [
            f
            for f in python_files
            if not str(f).startswith(str(self.project_root / "test"))
        ]

        for file_path in python_files[:10]:  # 限制处理文件数量
            try:
                test_cases = self.test_generator.generate_tests_for_file(file_path)
                if test_cases:
                    test_file_path = self._create_test_file(file_path, test_cases)
                    results["generated_tests"].append(
                        {
                            "source_file": str(file_path),
                            "test_file": str(test_file_path),
                            "test_count": len(test_cases),
                        }
                    )
            except Exception as e:
                logger.error(f"处理文件 {file_path} 失败: {e}")

        # 重新分析覆盖率
        final_coverage = self.coverage_analyzer.analyze_coverage()
        results["final_coverage"] = final_coverage

        # 计算改进
        improvement = (
            final_coverage.coverage_percentage - initial_coverage.coverage_percentage
        )
        results["improvement"] = improvement

        logger.info(f"覆盖率提升: {improvement:.1f}%")

        return results

    def _create_test_file(self, source_file: Path, test_cases: List[TestCase]) -> Path:
        """创建测试文件"""
        # 确定测试文件路径
        relative_path = source_file.relative_to(self.project_root)
        test_file_name = f"test_{source_file.stem}.py"
        test_file_path = self.project_root / "test" / "generated" / test_file_name

        # 创建测试目录
        test_file_path.parent.mkdir(parents=True, exist_ok=True)

        # 生成测试文件内容
        test_content = self._generate_test_file_content(test_cases)

        # 写入测试文件
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(test_content)

        logger.info(f"创建测试文件: {test_file_path}")

        return test_file_path

    def _generate_test_file_content(self, test_cases: List[TestCase]) -> str:
        """生成测试文件内容"""
        lines = []

        # 添加文件头
        lines.append('"""')
        lines.append("自动生成的测试文件")
        lines.append('"""')
        lines.append("")

        # 添加导入
        lines.append("import pytest")
        lines.append("import asyncio")
        lines.append("from unittest.mock import patch, MagicMock")
        lines.append("")

        # 收集所有导入
        all_imports = set()
        for test_case in test_cases:
            all_imports.update(test_case.imports)

        for import_stmt in sorted(all_imports):
            lines.append(import_stmt)

        lines.append("")
        lines.append("")

        # 添加测试类
        lines.append("class TestGeneratedTests:")
        lines.append('    """自动生成的测试类"""')
        lines.append("")

        # 添加测试方法
        for test_case in test_cases:
            lines.append(f"    # {test_case.description}")
            lines.extend(
                ["    " + line for line in test_case.test_code.strip().split("\n")]
            )
            lines.append("")

        return "\n".join(lines)

    def generate_coverage_report(self, results: Dict[str, Any]) -> str:
        """生成覆盖率报告"""
        report = []
        report.append("=" * 60)
        report.append("📊 测试覆盖率提升报告")
        report.append("=" * 60)

        # 初始覆盖率
        initial = results.get("initial_coverage")
        if initial:
            report.append(f"📈 初始覆盖率: {initial.coverage_percentage:.1f}%")
            report.append(f"   总行数: {initial.total_lines}")
            report.append(f"   已覆盖: {initial.covered_lines}")

        # 生成的测试
        generated_tests = results.get("generated_tests", [])
        if generated_tests:
            report.append(f"\n🧪 生成的测试文件: {len(generated_tests)} 个")
            total_tests = sum(t["test_count"] for t in generated_tests)
            report.append(f"   总测试用例: {total_tests} 个")

        # 最终覆盖率
        final = results.get("final_coverage")
        if final:
            report.append(f"\n📊 最终覆盖率: {final.coverage_percentage:.1f}%")
            improvement = results.get("improvement", 0)
            if improvement > 0:
                report.append(f"✅ 覆盖率提升: +{improvement:.1f}%")
            else:
                report.append(f"⚠️  覆盖率变化: {improvement:.1f}%")

        report.append("=" * 60)

        return "\n".join(report)


def main() -> None:
    """主函数"""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "."

    enhancer = TestCoverageEnhancer(project_root)

    try:
        # 提升测试覆盖率
        results = enhancer.enhance_test_coverage()

        # 生成并打印报告
        report = enhancer.generate_coverage_report(results)
        print(report)

        # 保存详细结果
        with open("test_coverage_report.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)

        logger.info("测试覆盖率报告已保存到: test_coverage_report.json")

    except Exception as e:
        logger.error(f"提升测试覆盖率失败: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
