#!/usr/bin/env python3.13

"""
无障碍服务快速验证脚本
用于日常开发中的快速检查

功能：
1. Python 版本检查
2. 必要文件检查
3. 基础依赖检查
4. 语法检查
5. 导入测试
6. 配置文件检查
7. 基础测试运行
"""

import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class QuickValidator:
    """快速验证器"""

    def __init__(self, service_path: str):
        self.service_path = Path(service_path)
        self.results = []
        self.start_time = time.time()

    def log_result(self, name: str, passed: bool, message: str, error: str = None):
        """记录测试结果"""
        status = "✅" if passed else "❌"
        print(f"{status} {name}: {message}")
        if error:
            print(f"   错误: {error}")

        self.results.append(
            {"name": name, "passed": passed, "message": message, "error": error}
        )

    def run_command(
        self, command: list[str], timeout: int = 10
    ) -> tuple[bool, str, str]:
        """运行命令"""
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

    def check_python_version(self) -> None:
        """检查 Python 版本"""
        version = platform.python_version()
        major, minor, patch = map(int, version.split("."))

        if major == 3 and minor >= 13:
            self.log_result("Python 版本", True, f"Python {version}")
        else:
            self.log_result("Python 版本", False, f"Python {version} (需要 3.13+)")

    def check_required_files(self) -> None:
        """检查必要文件"""
        required_files = [
            "pyproject.toml",
            "requirements.txt",
            "command/server/main.py",
            "config/config.py",
            "internal/service/app.py",
        ]

        missing_files = []
        for file_path in required_files:
            if not (self.service_path / file_path).exists():
                missing_files.append(file_path)

        if not missing_files:
            self.log_result(
                "必要文件", True, f"所有文件存在 ({len(required_files)} 个)"
            )
        else:
            self.log_result("必要文件", False, f"缺少文件: {', '.join(missing_files)}")

    def check_basic_dependencies(self) -> None:
        """检查基础依赖"""
        basic_deps = ["grpc", "pydantic", "yaml"]  # 修正模块名
        missing_deps = []

        # 优先使用本地虚拟环境的Python
        python_exe = sys.executable
        venv_python = self.service_path / ".venv" / "bin" / "python"
        if venv_python.exists():
            python_exe = str(venv_python)

        for dep in basic_deps:
            success, _, _ = self.run_command([python_exe, "-c", f"import {dep}"])
            if not success:
                missing_deps.append(dep)

        if not missing_deps:
            self.log_result("基础依赖", True, f"核心依赖已安装 ({len(basic_deps)} 个)")
        else:
            self.log_result("基础依赖", False, f"缺少依赖: {', '.join(missing_deps)}")

    def check_syntax(self) -> None:
        """检查语法"""
        python_files = list(self.service_path.rglob("*.py"))
        syntax_errors = 0
        checked_files = 0

        for py_file in python_files:
            if any(
                part in str(py_file)
                for part in [".venv", "__pycache__", ".pytest_cache"]
            ):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    compile(f.read(), str(py_file), "exec")
                checked_files += 1
            except (SyntaxError, UnicodeDecodeError):
                syntax_errors += 1

        if syntax_errors == 0:
            self.log_result("语法检查", True, f"语法正确 ({checked_files} 个文件)")
        else:
            self.log_result("语法检查", False, f"发现 {syntax_errors} 个语法错误")

    def check_imports(self) -> None:
        """检查导入"""
        sys.path.insert(0, str(self.service_path))

        core_modules = ["config.config", "internal.service.app"]
        import_errors = []

        for module in core_modules:
            try:
                __import__(module)
            except Exception as e:
                import_errors.append(f"{module}: {str(e)[:50]}...")

        if not import_errors:
            self.log_result(
                "导入测试", True, f"核心模块导入成功 ({len(core_modules)} 个)"
            )
        else:
            self.log_result("导入测试", False, f"导入失败: {len(import_errors)} 个模块")

    def check_config_file(self) -> None:
        """检查配置文件"""
        config_file = self.service_path / "config" / "config.yaml"

        if config_file.exists():
            try:
                import yaml

                with open(config_file, encoding="utf-8") as f:
                    yaml.safe_load(f)
                self.log_result("配置文件", True, "配置文件格式正确")
            except Exception as e:
                self.log_result("配置文件", False, f"配置文件错误: {str(e)[:50]}...")
        else:
            self.log_result("配置文件", False, "配置文件不存在")

    def run_basic_tests(self) -> None:
        """运行基础测试"""
        test_files = list(self.service_path.glob("test/test_*.py"))

        # 优先使用本地虚拟环境的Python
        python_exe = sys.executable
        venv_python = self.service_path / ".venv" / "bin" / "python"
        if venv_python.exists():
            python_exe = str(venv_python)

        if test_files:
            # 尝试运行一个简单的测试，只收集不执行，增加超时时间
            success, stdout, stderr = self.run_command(
                [
                    python_exe,
                    "-m",
                    "pytest",
                    "--collect-only",
                    "-q",
                    str(test_files[0]),
                ],
                timeout=30,  # 增加超时时间到30秒
            )

            if success:
                self.log_result("基础测试", True, "测试收集成功")
            else:
                self.log_result(
                    "基础测试",
                    False,
                    "测试运行失败",
                    stderr[:100] if stderr else "未知错误",
                )
        else:
            self.log_result("基础测试", False, "未找到测试文件")

    def run_all_checks(self) -> None:
        """运行所有检查"""
        print("🚀 开始快速验证...")
        print(f"📁 服务路径: {self.service_path}")
        print(f"🐍 Python 版本: {platform.python_version()}")
        print("-" * 50)

        # 运行所有检查
        self.check_python_version()
        self.check_required_files()
        self.check_basic_dependencies()
        self.check_syntax()
        self.check_imports()
        self.check_config_file()
        self.run_basic_tests()

        # 统计结果
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r["passed"])
        success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        duration = time.time() - self.start_time

        print("-" * 50)
        print("📊 验证完成!")
        print(f"✅ 通过: {passed_checks}/{total_checks} ({success_rate:.1f}%)")
        print(f"⏱️  耗时: {duration:.2f}s")

        # 保存简化报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "service_path": str(self.service_path),
            "python_version": platform.python_version(),
            "summary": {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "success_rate": success_rate,
                "duration": duration,
            },
            "results": self.results,
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"quick_validation_report_{timestamp}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📄 报告已保存: {report_file}")

        if success_rate < 100:
            print("\n💡 建议:")
            failed_checks = [r for r in self.results if not r["passed"]]
            for check in failed_checks:
                print(f"   - 修复 {check['name']}: {check['message']}")

        return success_rate == 100


def main() -> None:
    """主函数"""
    service_path = os.path.dirname(os.path.abspath(__file__))
    validator = QuickValidator(service_path)
    success = validator.run_all_checks()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
