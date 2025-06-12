#!/usr/bin/env python3
"""索克生活微服务语法检查工具"""

import ast
import logging
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SyntaxChecker:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues_fixed = 0
        self.files_processed = 0

        self.microservices = [
            "services/agent-services/xiaoai-service",
            "services/agent-services/xiaoke-service",
            "services/agent-services/laoke-service",
            "services/agent-services/soer-service",
            "services/ai-model-service",
            "services/api-gateway",
            "services/blockchain-service",
            "services/communication-service",
            "services/diagnostic-services",
            "services/unified-health-data-service",
            "services/unified-knowledge-service",
            "services/unified-support-service",
            "services/user-management-service",
            "services/utility-services",
        ]

    def find_python_files(self, service_path: Path) -> List[Path]:
        python_files = []
        if not service_path.exists():
            return python_files

        for py_file in service_path.rglob("*.py"):
            # 排除虚拟环境和缓存
            if any(
                part in str(py_file)
                for part in [".venv", "__pycache__", ".pytest_cache", ".ruff_cache"]
            ):
                continue
            python_files.append(py_file)
        return python_files

    def check_file_syntax(self, file_path: Path) -> List[str]:
        issues = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            ast.parse(content)
        except SyntaxError as e:
            issues.append(f"{file_path}:{e.lineno} - {e.msg}")
        except Exception as e:
            issues.append(f"{file_path} - 读取错误: {e}")
        return issues

    def fix_basic_syntax(self, file_path: Path) -> bool:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original = content

            # 基本修复
            lines = content.split("\n")
            fixed_lines = []

            for i, line in enumerate(lines):
                # 转换制表符为空格
                if "\t" in line:
                    line = line.expandtabs(4)

                # 修复基本缩进
                if line.strip() and i > 0:
                    prev_line = lines[i - 1].strip()
                    if (
                        prev_line.endswith(":")
                        and not line.startswith(" ")
                        and line.strip()
                    ):
                        line = "    " + line

                fixed_lines.append(line)

            content = "\n".join(fixed_lines)

            # 验证修复
            try:
                ast.parse(content)
                if content != original:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    self.issues_fixed += 1
                    return True
            except SyntaxError:
                pass

        except Exception as e:
            logger.error(f"修复失败 {file_path}: {e}")
        return False

    def scan_and_fix(self):
        logger.info("开始扫描微服务语法问题...")

        all_issues = []
        files_with_issues = []

        for service_name in self.microservices:
            service_path = self.project_root / service_name
            logger.info(f"检查: {service_name}")

            python_files = self.find_python_files(service_path)

            for py_file in python_files:
                issues = self.check_file_syntax(py_file)
                if issues:
                    all_issues.extend(issues)
                    files_with_issues.append(py_file)
                self.files_processed += 1

        logger.info(f"发现 {len(all_issues)} 个语法问题")

        # 尝试修复
        for file_path in files_with_issues:
            if self.fix_basic_syntax(file_path):
                logger.info(f"修复: {file_path}")

        print(f"\n摘要:")
        print(f"  处理文件: {self.files_processed}")
        print(f"  发现问题: {len(all_issues)}")
        print(f"  修复文件: {self.issues_fixed}")

        # 显示剩余问题
        if all_issues:
            print(f"\n剩余问题:")
            for issue in all_issues[:10]:
                print(f"  {issue}")


def main():
    checker = SyntaxChecker(".")
    checker.scan_and_fix()


if __name__ == "__main__":
    main()
