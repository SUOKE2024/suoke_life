#!/usr/bin/env python3
"""
索克生活无障碍服务 - 代码质量改进脚本

该脚本用于自动修复代码质量问题，包括：
1. 修复安全漏洞
2. 改进错误处理
3. 添加类型注解
4. 优化导入语句
5. 统一代码风格

遵循Python 3.13.3和最佳实践
"""

import ast
import json
import logging
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("code_quality_improvements.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class CodeQualityImprover:
    """代码质量改进器"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.improvements_report = {
            "timestamp": datetime.now().isoformat(),
            "fixed_files": [],
            "security_fixes": [],
            "error_handling_fixes": [],
            "type_annotation_fixes": [],
            "import_fixes": [],
            "style_fixes": [],
            "errors": [],
            "statistics": {
                "total_files_processed": 0,
                "total_fixes_applied": 0,
                "security_issues_fixed": 0,
                "error_handling_improved": 0,
            },
        }

    def fix_security_issues(self) -> None:
        """修复安全问题"""
        logger.info("🔒 开始修复安全问题...")

        # 查找使用pickle的文件
        pickle_files = self._find_files_with_pattern(
            r"import\s+pickle|from\s+pickle\s+import"
        )

        for file_path in pickle_files:
            self._fix_pickle_usage(file_path)

        # 查找明文密码存储
        password_files = self._find_files_with_pattern(
            r'password\s*=\s*["\'][^"\']*["\']'
        )

        for file_path in password_files:
            self._fix_password_storage(file_path)

    def _fix_pickle_usage(self, file_path: str) -> None:
        """修复pickle使用"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 替换pickle导入
            content = re.sub(
                r"import\s+pickle", "import json  # 替代pickle以提高安全性", content
            )

            # 替换pickle.loads
            content = re.sub(r"pickle\.loads\(", "json.loads(", content)

            # 替换pickle.dumps
            content = re.sub(r"pickle\.dumps\(", "json.dumps(", content)

            # 添加安全注释
            if "pickle" in content:
                content = f"""# 安全提示: 已将pickle替换为json以提高安全性
# pickle反序列化可能导致代码执行漏洞
{content}"""

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            self.improvements_report["security_fixes"].append(
                {"file": file_path, "issue": "pickle使用", "fix": "替换为json"}
            )
            self.improvements_report["statistics"]["security_issues_fixed"] += 1

            logger.info(f"✅ 已修复pickle使用: {file_path}")

        except Exception as e:
            error_msg = f"修复pickle使用失败 {file_path}: {e}"
            logger.error(error_msg)
            self.improvements_report["errors"].append(error_msg)

    def _fix_password_storage(self, file_path: str) -> None:
        """修复密码存储"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 替换明文密码
            content = re.sub(
                r'password\s*=\s*["\'][^"\']*["\']',
                'password = os.getenv("PASSWORD", "")  # 使用环境变量存储密码',
                content,
            )

            # 添加os导入如果不存在
            if "import os" not in content and "from os import" not in content:
                content = f"import os\n{content}"

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            self.improvements_report["security_fixes"].append(
                {"file": file_path, "issue": "明文密码存储", "fix": "使用环境变量"}
            )
            self.improvements_report["statistics"]["security_issues_fixed"] += 1

            logger.info(f"✅ 已修复密码存储: {file_path}")

        except Exception as e:
            error_msg = f"修复密码存储失败 {file_path}: {e}"
            logger.error(error_msg)
            self.improvements_report["errors"].append(error_msg)

    def improve_error_handling(self) -> None:
        """改进错误处理"""
        logger.info("🛠️ 开始改进错误处理...")

        # 查找使用通用Exception的文件
        exception_files = self._find_files_with_pattern(r"except\s+Exception\s*:")

        for file_path in exception_files:
            self._improve_exception_handling(file_path)

    def _improve_exception_handling(self, file_path: str) -> None:
        """改进异常处理"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 改进通用异常处理
            improved_content = re.sub(
                r"except\s+Exception\s*:", "except Exception as e:", content
            )

            # 添加日志记录
            improved_content = re.sub(
                r"except\s+Exception\s+as\s+e\s*:\s*\n(\s*)pass",
                r'except Exception as e:\n\1logger.exception(f"操作失败: {e}")\n\1raise',
                improved_content,
            )

            if improved_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(improved_content)

                self.improvements_report["error_handling_fixes"].append(
                    {"file": file_path, "fix": "改进异常处理和日志记录"}
                )
                self.improvements_report["statistics"]["error_handling_improved"] += 1

                logger.info(f"✅ 已改进错误处理: {file_path}")

        except Exception as e:
            error_msg = f"改进错误处理失败 {file_path}: {e}"
            logger.error(error_msg)
            self.improvements_report["errors"].append(error_msg)

    def add_type_annotations(self) -> None:
        """添加类型注解"""
        logger.info("📝 开始添加类型注解...")

        python_files = list(self.base_path.glob("**/*.py"))

        for file_path in python_files:
            if self._should_skip_file(str(file_path)):
                continue

            self._add_type_annotations_to_file(str(file_path))

    def _add_type_annotations_to_file(self, file_path: str) -> None:
        """为文件添加类型注解"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 解析AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return  # 跳过语法错误的文件

            # 查找缺少类型注解的函数
            functions_without_annotations = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.returns and not node.name.startswith("_"):
                        functions_without_annotations.append(node.name)

            if functions_without_annotations:
                # 添加基本的类型注解
                improved_content = self._add_basic_type_annotations(content)

                if improved_content != content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(improved_content)

                    self.improvements_report["type_annotation_fixes"].append(
                        {"file": file_path, "functions": functions_without_annotations}
                    )

                    logger.info(f"✅ 已添加类型注解: {file_path}")

        except Exception as e:
            error_msg = f"添加类型注解失败 {file_path}: {e}"
            logger.error(error_msg)
            self.improvements_report["errors"].append(error_msg)

    def _add_basic_type_annotations(self, content: str) -> str:
        """添加基本类型注解"""
        # 为常见函数模式添加类型注解
        patterns = [
            (r"def\s+(\w+)\(self\)\s*:", r"def \1(self) -> None:"),
            (
                r"def\s+(\w+)\(self,\s*\*args,\s*\*\*kwargs\)\s*:",
                r"def \1(self, *args, **kwargs) -> Any:",
            ),
            (r"def\s+main\(\)\s*:", r"def main() -> None:"),
            (r"def\s+(\w+)\(\)\s*:", r"def \1() -> None:"),
        ]

        improved_content = content
        for pattern, replacement in patterns:
            improved_content = re.sub(pattern, replacement, improved_content)

        # 添加必要的导入
        if (
            "-> Any:" in improved_content
            and "from typing import" not in improved_content
        ):
            improved_content = f"from typing import Any\n{improved_content}"

        return improved_content

    def optimize_imports(self) -> None:
        """优化导入语句"""
        logger.info("📦 开始优化导入语句...")

        python_files = list(self.base_path.glob("**/*.py"))

        for file_path in python_files:
            if self._should_skip_file(str(file_path)):
                continue

            self._optimize_imports_in_file(str(file_path))

    def _optimize_imports_in_file(self, file_path: str) -> None:
        """优化文件中的导入语句"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 移除未使用的导入
            lines = content.split("\n")
            optimized_lines = []

            for line in lines:
                # 检查是否是导入语句
                if line.strip().startswith("import ") or line.strip().startswith(
                    "from "
                ):
                    # 简单的未使用导入检测
                    if self._is_import_used(line, content):
                        optimized_lines.append(line)
                    else:
                        logger.info(f"移除未使用的导入: {line.strip()} in {file_path}")
                else:
                    optimized_lines.append(line)

            optimized_content = "\n".join(optimized_lines)

            if optimized_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(optimized_content)

                self.improvements_report["import_fixes"].append(
                    {"file": file_path, "fix": "移除未使用的导入"}
                )

        except Exception as e:
            error_msg = f"优化导入失败 {file_path}: {e}"
            logger.error(error_msg)
            self.improvements_report["errors"].append(error_msg)

    def _is_import_used(self, import_line: str, content: str) -> bool:
        """检查导入是否被使用"""
        # 简单的使用检测逻辑
        if "import " in import_line:
            if import_line.strip().startswith("from "):
                # from module import name
                match = re.search(r"from\s+\S+\s+import\s+(\w+)", import_line)
                if match:
                    imported_name = match.group(1)
                    return imported_name in content.replace(import_line, "")
            else:
                # import module
                match = re.search(r"import\s+(\w+)", import_line)
                if match:
                    module_name = match.group(1)
                    return f"{module_name}." in content.replace(import_line, "")

        return True  # 默认保留

    def apply_code_formatting(self) -> None:
        """应用代码格式化"""
        logger.info("🎨 开始应用代码格式化...")

        try:
            # 使用black格式化代码
            result = subprocess.run(
                ["python", "-m", "black", "--line-length", "88", "."],
                capture_output=True,
                text=True,
                cwd=self.base_path,
            )

            if result.returncode == 0:
                logger.info("✅ Black格式化完成")
                self.improvements_report["style_fixes"].append(
                    {"tool": "black", "status": "success"}
                )
            else:
                logger.warning(f"Black格式化警告: {result.stderr}")

        except FileNotFoundError:
            logger.warning("Black未安装，跳过格式化")

        try:
            # 使用isort整理导入
            result = subprocess.run(
                ["python", "-m", "isort", "."],
                capture_output=True,
                text=True,
                cwd=self.base_path,
            )

            if result.returncode == 0:
                logger.info("✅ isort导入整理完成")
                self.improvements_report["style_fixes"].append(
                    {"tool": "isort", "status": "success"}
                )
            else:
                logger.warning(f"isort警告: {result.stderr}")

        except FileNotFoundError:
            logger.warning("isort未安装，跳过导入整理")

    def _find_files_with_pattern(self, pattern: str) -> List[str]:
        """查找包含特定模式的文件"""
        matching_files = []

        for file_path in self.base_path.glob("**/*.py"):
            if self._should_skip_file(str(file_path)):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                if re.search(pattern, content):
                    matching_files.append(str(file_path))

            except Exception as e:
                logger.warning(f"读取文件失败 {file_path}: {e}")

        return matching_files

    def _should_skip_file(self, file_path: str) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = [
            ".venv/",
            "__pycache__/",
            ".git/",
            "node_modules/",
            ".pytest_cache/",
            ".ruff_cache/",
            "build/",
            "dist/",
            ".egg-info/",
        ]

        return any(pattern in file_path for pattern in skip_patterns)

    def generate_report(self) -> None:
        """生成改进报告"""
        report_file = (
            f"code_quality_improvements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(self.improvements_report, f, indent=2, ensure_ascii=False)

            logger.info(f"📊 改进报告已生成: {report_file}")

            # 打印统计信息
            stats = self.improvements_report["statistics"]
            logger.info("📈 改进统计:")
            logger.info(f"   处理文件数: {stats['total_files_processed']}")
            logger.info(f"   应用修复数: {stats['total_fixes_applied']}")
            logger.info(f"   安全问题修复: {stats['security_issues_fixed']}")
            logger.info(f"   错误处理改进: {stats['error_handling_improved']}")

            if self.improvements_report["errors"]:
                logger.warning(
                    f"⚠️  发生 {len(self.improvements_report['errors'])} 个错误"
                )

        except Exception as e:
            logger.error(f"生成报告失败: {e}")

    def run_improvements(self) -> None:
        """执行完整的代码质量改进流程"""
        logger.info("🚀 开始执行代码质量改进...")

        try:
            self.fix_security_issues()
            self.improve_error_handling()
            self.add_type_annotations()
            self.optimize_imports()
            self.apply_code_formatting()

            logger.info("✅ 代码质量改进完成")

        except Exception as e:
            logger.error(f"改进过程中发生错误: {e}")
            self.improvements_report["errors"].append(str(e))

        finally:
            self.generate_report()


def main() -> None:
    """主函数"""
    print("🛠️ 索克生活无障碍服务 - 代码质量改进工具")
    print("=" * 50)

    # 确认改进操作
    response = input("⚠️  此操作将修改代码文件，是否继续？(y/N): ")
    if response.lower() != "y":
        print("❌ 改进操作已取消")
        return

    # 执行改进
    improver = CodeQualityImprover()
    improver.run_improvements()

    print("🎉 代码质量改进完成！请查看生成的报告文件了解详情。")


if __name__ == "__main__":
    main()
