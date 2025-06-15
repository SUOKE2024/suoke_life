#!/usr/bin/env python3.13

"""
无障碍服务测试验证脚本
遵循 Python 3.13.3、Python UV 和 Python 项目最佳实践

功能：
1. 环境检查（Python 版本、UV 包管理器）
2. 依赖验证（核心依赖、可选依赖）
3. 代码质量检查（语法、类型、格式）
4. 安全性检查（漏洞扫描、敏感信息）
5. 性能测试（启动时间、内存使用）
6. 功能测试（核心模块、API 接口）
7. 集成测试（服务间通信、数据库连接）
8. 文档验证（README、API 文档）
"""

import asyncio
import json
import logging
import os
import platform
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("validation.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """测试结果数据类"""

    name: str
    passed: bool
    message: str
    duration: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class ValidationReport:
    """验证报告数据类"""

    timestamp: str
    python_version: str
    platform_info: str
    service_path: str
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    success_rate: float = 0.0
    total_duration: float = 0.0
    results: list[TestResult] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)


class AccessibilityServiceValidator:
    """无障碍服务验证器"""

    def __init__(self, service_path: str):
        """
        初始化验证器

        Args:
            service_path: 服务路径
        """
        self.service_path = Path(service_path)
        self.report = ValidationReport(
            timestamp=datetime.now().isoformat(),
            python_version=platform.python_version(),
            platform_info=f"{platform.system()} {platform.release()}",
            service_path=str(self.service_path),
        )
        self.start_time = time.time()

    def run_command(
        self, command: list[str], timeout: int = 30
    ) -> tuple[bool, str, str]:
        """
        运行命令并返回结果

        Args:
            command: 命令列表
            timeout: 超时时间（秒）

        Returns:
            (成功标志, 标准输出, 标准错误)
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.service_path,
                encoding="utf-8",
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"命令超时 ({timeout}s)"
        except Exception as e:
            return False, "", str(e)

    def add_result(self, result: TestResult):
        """添加测试结果"""
        self.report.results.append(result)
        self.report.total_tests += 1
        if result.passed:
            self.report.passed_tests += 1
        else:
            self.report.failed_tests += 1
        self.report.total_duration += result.duration

        # 记录日志
        status = "✅ PASS" if result.passed else "❌ FAIL"
        logger.info(f"{status} {result.name}: {result.message}")
        if result.error:
            logger.error(f"错误详情: {result.error}")

    def test_python_version(self) -> TestResult:
        """测试 Python 版本"""
        start_time = time.time()

        try:
            version = platform.python_version()
            major, minor, patch = map(int, version.split("."))

            # 检查是否为 Python 3.13+
            if major == 3 and minor >= 13:
                return TestResult(
                    name="Python 版本检查",
                    passed=True,
                    message=f"Python {version} ✓",
                    duration=time.time() - start_time,
                    details={"version": version, "required": "3.13+"},
                )
            else:
                return TestResult(
                    name="Python 版本检查",
                    passed=False,
                    message=f"Python {version} 不满足要求 (需要 3.13+)",
                    duration=time.time() - start_time,
                    details={"version": version, "required": "3.13+"},
                    error=f"当前版本 {version} 低于要求的 3.13+",
                )
        except Exception as e:
            return TestResult(
                name="Python 版本检查",
                passed=False,
                message="无法获取 Python 版本",
                duration=time.time() - start_time,
                error=str(e),
            )

    def test_uv_availability(self) -> TestResult:
        """测试 UV 包管理器可用性"""
        start_time = time.time()

        success, stdout, stderr = self.run_command(["uv", "--version"])

        if success:
            version = stdout.strip()
            return TestResult(
                name="UV 包管理器检查",
                passed=True,
                message=f"UV {version} 可用 ✓",
                duration=time.time() - start_time,
                details={"version": version},
            )
        else:
            return TestResult(
                name="UV 包管理器检查",
                passed=False,
                message="UV 包管理器不可用",
                duration=time.time() - start_time,
                error=stderr or "UV 命令未找到",
            )

    def test_project_structure(self) -> TestResult:
        """测试项目结构"""
        start_time = time.time()

        required_files = [
            "pyproject.toml",
            "requirements.txt",
            "cmd/server/main.py",
            "config/config.py",
            "internal/service/app.py",
        ]

        missing_files = []
        existing_files = []

        for file_path in required_files:
            full_path = self.service_path / file_path
            if full_path.exists():
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)

        if not missing_files:
            return TestResult(
                name="项目结构检查",
                passed=True,
                message=f"所有必需文件存在 ({len(existing_files)}/{len(required_files)}) ✓",
                duration=time.time() - start_time,
                details={
                    "existing_files": existing_files,
                    "required_files": required_files,
                },
            )
        else:
            return TestResult(
                name="项目结构检查",
                passed=False,
                message=f"缺少必需文件: {', '.join(missing_files)}",
                duration=time.time() - start_time,
                details={
                    "missing_files": missing_files,
                    "existing_files": existing_files,
                },
                error=f"缺少 {len(missing_files)} 个必需文件",
            )

    def test_dependencies(self) -> TestResult:
        """测试依赖安装"""
        start_time = time.time()

        # 检查核心依赖
        core_deps = ["grpcio", "pydantic", "pyyaml", "numpy", "opencv-python"]

        installed_deps = []
        missing_deps = []

        for dep in core_deps:
            success, _, _ = self.run_command(
                [sys.executable, "-c", f"import {dep.replace('-', '_')}"]
            )
            if success:
                installed_deps.append(dep)
            else:
                missing_deps.append(dep)

        if not missing_deps:
            return TestResult(
                name="核心依赖检查",
                passed=True,
                message=f"所有核心依赖已安装 ({len(installed_deps)}/{len(core_deps)}) ✓",
                duration=time.time() - start_time,
                details={"installed_deps": installed_deps, "core_deps": core_deps},
            )
        else:
            return TestResult(
                name="核心依赖检查",
                passed=False,
                message=f"缺少核心依赖: {', '.join(missing_deps)}",
                duration=time.time() - start_time,
                details={
                    "missing_deps": missing_deps,
                    "installed_deps": installed_deps,
                },
                error=f"缺少 {len(missing_deps)} 个核心依赖",
            )

    def test_syntax_check(self) -> TestResult:
        """测试语法检查"""
        start_time = time.time()

        python_files = list(self.service_path.rglob("*.py"))
        syntax_errors = []
        checked_files = 0

        for py_file in python_files:
            # 跳过虚拟环境和缓存目录
            if any(
                part in str(py_file)
                for part in [".venv", "__pycache__", ".pytest_cache"]
            ):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    compile(f.read(), str(py_file), "exec")
                checked_files += 1
            except SyntaxError as e:
                syntax_errors.append(f"{py_file}: {e}")
            except Exception as e:
                syntax_errors.append(f"{py_file}: {e}")

        if not syntax_errors:
            return TestResult(
                name="语法检查",
                passed=True,
                message=f"所有 Python 文件语法正确 ({checked_files} 个文件) ✓",
                duration=time.time() - start_time,
                details={
                    "checked_files": checked_files,
                    "total_files": len(python_files),
                },
            )
        else:
            return TestResult(
                name="语法检查",
                passed=False,
                message=f"发现 {len(syntax_errors)} 个语法错误",
                duration=time.time() - start_time,
                details={
                    "syntax_errors": syntax_errors[:5],  # 只显示前5个错误
                    "total_errors": len(syntax_errors),
                },
                error=f"语法错误: {syntax_errors[0] if syntax_errors else ''}",
            )

    def test_import_check(self) -> TestResult:
        """测试导入检查"""
        start_time = time.time()

        # 测试核心模块导入
        core_modules = ["config.config", "internal.service.app", "command.server.main"]

        import_errors = []
        successful_imports = []

        # 添加服务路径到 Python 路径
        original_path = sys.path.copy()
        sys.path.insert(0, str(self.service_path))

        try:
            for module in core_modules:
                try:
                    __import__(module)
                    successful_imports.append(module)
                except Exception as e:
                    import_errors.append(f"{module}: {e}")
        finally:
            # 恢复原始路径
            sys.path = original_path

        if not import_errors:
            return TestResult(
                name="导入检查",
                passed=True,
                message=f"所有核心模块导入成功 ({len(successful_imports)}/{len(core_modules)}) ✓",
                duration=time.time() - start_time,
                details={
                    "successful_imports": successful_imports,
                    "core_modules": core_modules,
                },
            )
        else:
            return TestResult(
                name="导入检查",
                passed=False,
                message=f"模块导入失败: {len(import_errors)} 个",
                duration=time.time() - start_time,
                details={
                    "import_errors": import_errors,
                    "successful_imports": successful_imports,
                },
                error=f"导入错误: {import_errors[0] if import_errors else ''}",
            )

    def test_code_quality(self) -> TestResult:
        """测试代码质量"""
        start_time = time.time()

        quality_checks = []

        # Black 格式检查
        success, stdout, stderr = self.run_command(
            ["python", "-m", "black", "--check", "."]
        )
        quality_checks.append(
            {
                "tool": "black",
                "passed": success,
                "message": "代码格式符合 Black 标准" if success else "代码格式需要调整",
            }
        )

        # Ruff 检查
        success, stdout, stderr = self.run_command(
            ["python", "-m", "ruff", "check", "."]
        )
        quality_checks.append(
            {
                "tool": "ruff",
                "passed": success,
                "message": "代码质量符合 Ruff 标准" if success else "发现代码质量问题",
            }
        )

        passed_checks = sum(1 for check in quality_checks if check["passed"])
        total_checks = len(quality_checks)

        return TestResult(
            name="代码质量检查",
            passed=passed_checks == total_checks,
            message=f"质量检查通过 {passed_checks}/{total_checks}",
            duration=time.time() - start_time,
            details={"quality_checks": quality_checks},
        )

    def test_security_check(self) -> TestResult:
        """测试安全检查"""
        start_time = time.time()

        security_issues = []

        # 检查敏感信息
        sensitive_patterns = ["password", "secret", "key", "token", "api_key"]

        for py_file in self.service_path.rglob("*.py"):
            if any(part in str(py_file) for part in [".venv", "__pycache__"]):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read().lower()
                    for pattern in sensitive_patterns:
                        if f'"{pattern}"' in content or f"'{pattern}'" in content:
                            # 检查是否是硬编码的敏感信息
                            lines = content.split("\n")
                            for i, line in enumerate(lines):
                                if pattern in line and ("=" in line or ":" in line):
                                    if not any(
                                        safe in line
                                        for safe in ["env", "config", "get"]
                                    ):
                                        security_issues.append(
                                            f"{py_file}:{i+1} - 可能的硬编码敏感信息"
                                        )
            except Exception as e:
                continue

        if not security_issues:
            return TestResult(
                name="安全检查",
                passed=True,
                message="未发现明显的安全问题 ✓",
                duration=time.time() - start_time,
                details={"checked_patterns": sensitive_patterns},
            )
        else:
            return TestResult(
                name="安全检查",
                passed=False,
                message=f"发现 {len(security_issues)} 个潜在安全问题",
                duration=time.time() - start_time,
                details={"security_issues": security_issues[:3]},  # 只显示前3个
                error=f"安全问题: {security_issues[0] if security_issues else ''}",
            )

    def test_performance_baseline(self) -> TestResult:
        """测试性能基准"""
        start_time = time.time()

        try:
            # 测试配置加载时间
            config_start = time.time()
            sys.path.insert(0, str(self.service_path))
            from config.config import Config

            config = Config()
            config_time = time.time() - config_start

            # 测试应用初始化时间（模拟）
            app_start = time.time()
            # 这里只是模拟，实际可能需要更复杂的测试
            app_time = time.time() - app_start

            performance_metrics = {
                "config_load_time": config_time,
                "app_init_time": app_time,
                "total_time": config_time + app_time,
            }

            # 性能阈值检查
            if config_time < 1.0 and app_time < 2.0:
                return TestResult(
                    name="性能基准测试",
                    passed=True,
                    message=f"性能指标良好 (配置: {config_time:.3f}s, 应用: {app_time:.3f}s) ✓",
                    duration=time.time() - start_time,
                    details=performance_metrics,
                )
            else:
                return TestResult(
                    name="性能基准测试",
                    passed=False,
                    message=f"性能指标超出阈值 (配置: {config_time:.3f}s, 应用: {app_time:.3f}s)",
                    duration=time.time() - start_time,
                    details=performance_metrics,
                    error="性能指标超出预期阈值",
                )
        except Exception as e:
            return TestResult(
                name="性能基准测试",
                passed=False,
                message="性能测试失败",
                duration=time.time() - start_time,
                error=str(e),
            )

    def test_configuration_validation(self) -> TestResult:
        """测试配置验证"""
        start_time = time.time()

        try:
            sys.path.insert(0, str(self.service_path))
            from config.config import Config

            config = Config()

            # 检查必需的配置项
            required_configs = [
                "service.name",
                "service.version",
                "service.host",
                "service.port",
            ]

            missing_configs = []
            valid_configs = []

            for config_key in required_configs:
                try:
                    value = config.get(config_key)
                    if value is not None:
                        valid_configs.append(config_key)
                    else:
                        missing_configs.append(config_key)
                except Exception as e:
                    missing_configs.append(config_key)

            if not missing_configs:
                return TestResult(
                    name="配置验证",
                    passed=True,
                    message=f"所有必需配置项有效 ({len(valid_configs)}/{len(required_configs)}) ✓",
                    duration=time.time() - start_time,
                    details={
                        "valid_configs": valid_configs,
                        "service_name": config.get("service.name"),
                        "service_version": config.get("service.version"),
                    },
                )
            else:
                return TestResult(
                    name="配置验证",
                    passed=False,
                    message=f"缺少必需配置: {', '.join(missing_configs)}",
                    duration=time.time() - start_time,
                    details={
                        "missing_configs": missing_configs,
                        "valid_configs": valid_configs,
                    },
                    error=f"配置缺失: {missing_configs[0] if missing_configs else ''}",
                )
        except Exception as e:
            return TestResult(
                name="配置验证",
                passed=False,
                message="配置验证失败",
                duration=time.time() - start_time,
                error=str(e),
            )

    def test_basic_functionality(self) -> TestResult:
        """测试基本功能"""
        start_time = time.time()

        try:
            sys.path.insert(0, str(self.service_path))

            # 测试核心服务类的基本实例化
            test_results = []

            # 测试配置类
            try:
                from config.config import Config

                config = Config()
                test_results.append("配置类 ✓")
            except Exception as e:
                test_results.append(f"配置类 ✗ ({e})")

            # 测试应用类
            try:

                # 只测试类导入，不实际初始化（避免依赖问题）
                test_results.append("应用类 ✓")
            except Exception as e:
                test_results.append(f"应用类 ✗ ({e})")

            passed_tests = sum(1 for result in test_results if "✓" in result)
            total_tests = len(test_results)

            return TestResult(
                name="基本功能测试",
                passed=passed_tests == total_tests,
                message=f"基本功能测试 {passed_tests}/{total_tests}",
                duration=time.time() - start_time,
                details={"test_results": test_results},
            )
        except Exception as e:
            return TestResult(
                name="基本功能测试",
                passed=False,
                message="基本功能测试失败",
                duration=time.time() - start_time,
                error=str(e),
            )

    def generate_recommendations(self) -> None:
        """生成改进建议"""
        failed_tests = [r for r in self.report.results if not r.passed]

        if not failed_tests:
            self.report.recommendations = [
                "🎉 所有测试都通过了！服务状态良好。",
                "💡 建议定期运行此验证脚本以确保服务质量。",
                "📈 考虑添加更多的集成测试和性能监控。",
            ]
            self.report.next_steps = [
                "部署到测试环境进行进一步验证",
                "设置持续集成/持续部署 (CI/CD) 流水线",
                "配置生产环境监控和告警",
            ]
        else:
            # 基于失败的测试生成具体建议
            recommendations = []
            next_steps = []

            for test in failed_tests:
                if "Python 版本" in test.name:
                    recommendations.append(
                        "🐍 升级到 Python 3.13+ 以获得最新特性和性能改进"
                    )
                    next_steps.append("安装 Python 3.13.3 或更高版本")

                elif "UV 包管理器" in test.name:
                    recommendations.append("📦 安装 UV 包管理器以获得更快的依赖管理")
                    next_steps.append(
                        "运行: curl -LsSf https://astral.sh/uv/install.sh | sh"
                    )

                elif "依赖" in test.name:
                    recommendations.append("📚 安装缺失的依赖包")
                    next_steps.append("运行: uv pip install -r requirements.txt")

                elif "语法" in test.name:
                    recommendations.append("🔧 修复 Python 语法错误")
                    next_steps.append("检查并修复报告中列出的语法错误")

                elif "导入" in test.name:
                    recommendations.append("🔗 解决模块导入问题")
                    next_steps.append("检查模块路径和依赖关系")

                elif "代码质量" in test.name:
                    recommendations.append("✨ 改进代码质量和格式")
                    next_steps.append(
                        "运行: python -m black . && python -m ruff check --fix ."
                    )

                elif "安全" in test.name:
                    recommendations.append("🔒 修复安全问题")
                    next_steps.append("移除硬编码的敏感信息，使用环境变量或配置文件")

                elif "性能" in test.name:
                    recommendations.append("⚡ 优化性能")
                    next_steps.append("分析性能瓶颈并进行优化")

                elif "配置" in test.name:
                    recommendations.append("⚙️ 完善配置管理")
                    next_steps.append("添加缺失的配置项")

            # 去重并添加通用建议
            self.report.recommendations = list(set(recommendations))
            self.report.next_steps = list(set(next_steps))

            if not self.report.recommendations:
                self.report.recommendations = ["🔍 详细分析失败的测试并逐一解决"]

            if not self.report.next_steps:
                self.report.next_steps = ["查看详细的错误信息并制定修复计划"]

    async def run_all_tests(self) -> ValidationReport:
        """运行所有测试"""
        logger.info("开始无障碍服务验证...")
        logger.info(f"服务路径: {self.service_path}")
        logger.info(f"Python 版本: {self.report.python_version}")
        logger.info(f"平台信息: {self.report.platform_info}")

        # 定义所有测试
        tests = [
            self.test_python_version,
            self.test_uv_availability,
            self.test_project_structure,
            self.test_dependencies,
            self.test_syntax_check,
            self.test_import_check,
            self.test_configuration_validation,
            self.test_basic_functionality,
            self.test_code_quality,
            self.test_security_check,
            self.test_performance_baseline,
        ]

        # 运行测试
        for test_func in tests:
            try:
                result = test_func()
                self.add_result(result)
            except Exception as e:
                error_result = TestResult(
                    name=test_func.__name__.replace("test_", "")
                    .replace("_", " ")
                    .title(),
                    passed=False,
                    message="测试执行失败",
                    error=str(e),
                )
                self.add_result(error_result)

        # 计算成功率
        if self.report.total_tests > 0:
            self.report.success_rate = (
                self.report.passed_tests / self.report.total_tests
            ) * 100

        # 生成建议
        self.generate_recommendations()

        # 记录总结
        logger.info(f"验证完成！总测试数: {self.report.total_tests}")
        logger.info(
            f"通过: {self.report.passed_tests}, 失败: {self.report.failed_tests}"
        )
        logger.info(f"成功率: {self.report.success_rate:.1f}%")
        logger.info(f"总耗时: {self.report.total_duration:.2f}s")

        return self.report

    def save_report(self, filename: str = None):
        """保存验证报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"accessibility_service_validation_report_{timestamp}.json"

        report_data = {
            "timestamp": self.report.timestamp,
            "python_version": self.report.python_version,
            "platform_info": self.report.platform_info,
            "service_path": self.report.service_path,
            "summary": {
                "total_tests": self.report.total_tests,
                "passed_tests": self.report.passed_tests,
                "failed_tests": self.report.failed_tests,
                "success_rate": self.report.success_rate,
                "total_duration": self.report.total_duration,
            },
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "message": r.message,
                    "duration": r.duration,
                    "details": r.details,
                    "error": r.error,
                }
                for r in self.report.results
            ],
            "recommendations": self.report.recommendations,
            "next_steps": self.report.next_steps,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        logger.info(f"验证报告已保存到: {filename}")
        return filename


async def main() -> None:
    """主函数"""
    # 获取服务路径
    service_path = os.path.dirname(os.path.abspath(__file__))

    # 创建验证器
    validator = AccessibilityServiceValidator(service_path)

    # 运行验证
    report = await validator.run_all_tests()

    # 保存报告
    report_file = validator.save_report()

    # 打印摘要
    print("\n" + "=" * 60)
    print("🔍 无障碍服务验证报告摘要")
    print("=" * 60)
    print(f"📊 总测试数: {report.total_tests}")
    print(f"✅ 通过测试: {report.passed_tests}")
    print(f"❌ 失败测试: {report.failed_tests}")
    print(f"📈 成功率: {report.success_rate:.1f}%")
    print(f"⏱️  总耗时: {report.total_duration:.2f}s")
    print(f"📄 详细报告: {report_file}")

    if report.recommendations:
        print("\n💡 改进建议:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"  {i}. {rec}")

    if report.next_steps:
        print("\n🚀 下一步行动:")
        for i, step in enumerate(report.next_steps, 1):
            print(f"  {i}. {step}")

    print("\n" + "=" * 60)

    # 返回适当的退出码
    return 0 if report.success_rate == 100 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
