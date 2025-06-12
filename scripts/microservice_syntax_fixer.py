#!/usr/bin/env python3
"""
索克生活微服务语法错误修复工具
基于项目现有代码结构及具体实现，洞察微服务语法错误并修复
"""

import argparse
import ast
import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class SyntaxErrorInfo:
    """语法错误数据类"""

    file: str
    line: int
    column: int
    message: str
    text: str
    error_type: str = "SyntaxError"


class MicroserviceSyntaxFixer:
    """微服务语法错误修复器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.errors_fixed = 0
        self.files_processed = 0

        # 微服务路径
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

    def load_known_errors(self) -> List[SyntaxErrorInfo]:
        """加载已知的语法错误"""
        errors = []
        error_file = self.project_root / "xiaoai_syntax_errors.json"

        if error_file.exists():
            try:
                with open(error_file, "r", encoding="utf-8") as f:
                    error_data = json.load(f)

                for error in error_data:
                    errors.append(
                        SyntaxErrorInfo(
                            file=error["file"],
                            line=error["line"],
                            column=error["column"],
                            message=error["message"],
                            text=error["text"],
                        )
                    )

                logger.info(f"加载了 {len(errors)} 个已知语法错误")
            except Exception as e:
                logger.error(f"加载错误文件失败: {e}")

        return errors

    def fix_indentation_errors(self, file_path: Path, content: str) -> str:
        """修复缩进错误"""
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            # 修复unexpected indent
            if line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                # 检查是否应该缩进
                if i > 0:
                    prev_line = lines[i - 1].strip()
                    if (
                        prev_line.endswith(":")
                        or prev_line.startswith("def ")
                        or prev_line.startswith("class ")
                        or prev_line.startswith("if ")
                        or prev_line.startswith("for ")
                        or prev_line.startswith("while ")
                        or prev_line.startswith("try:")
                        or prev_line.startswith("except ")
                        or prev_line.startswith("with ")
                    ):
                        line = "    " + line  # 添加4个空格缩进

            # 修复expected indented block
            if line.strip() == "pass" and i > 0:
                prev_line = lines[i - 1].strip()
                if prev_line.endswith(":"):
                    line = "    pass"  # 确保pass有正确缩进

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def fix_import_errors(self, content: str) -> str:
        """修复import语句错误"""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # 修复多个import在同一行的问题
            if "from dataclasses import dataclass from typing import" in line:
                fixed_lines.append("from dataclasses import dataclass")
                fixed_lines.append("from typing import Any")
                continue

            # 修复缩进的import语句
            if line.strip().startswith("from ") or line.strip().startswith("import "):
                if line.startswith("    ") or line.startswith("\t"):
                    # 移除import语句前的缩进
                    line = line.strip()

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def fix_assignment_expression_errors(self, content: str) -> str:
        """修复赋值表达式错误"""
        # 修复在函数调用中的赋值错误
        content = re.sub(
            r"EventBus\(backend=\'kafka\', self\.config=\{\}\)",
            "EventBus(backend='kafka', config={})",
            content,
        )

        # 修复logging格式字符串赋值错误
        content = re.sub(r"self\.format=\'([^\']+)\'", r"self.format = \'\1\'", content)

        return content

    def fix_file_syntax_errors(self, file_path: Path) -> bool:
        """修复单个文件的语法错误"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # 应用各种修复
            content = self.fix_indentation_errors(file_path, content)
            content = self.fix_import_errors(content)
            content = self.fix_assignment_expression_errors(content)

            # 验证修复后的语法
            try:
                ast.parse(content)

                # 只有在内容发生变化时才写入
                if content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    logger.info(f"成功修复文件: {file_path}")
                    self.errors_fixed += 1
                    return True

            except SyntaxError as e:
                logger.error(f"文件修复后仍有语法错误 {file_path}: {e}")
                return False

        except Exception as e:
            logger.error(f"修复文件失败 {file_path}: {e}")
            return False

        return False

    def fix_known_errors(self, errors: List[SyntaxErrorInfo]):
        """修复已知的语法错误"""
        files_to_fix = set()

        for error in errors:
            file_path = self.project_root / error.file
            if file_path.exists():
                files_to_fix.add(file_path)
            else:
                logger.warning(f"错误文件不存在: {error.file}")

        logger.info(f"需要修复 {len(files_to_fix)} 个文件")

        for file_path in files_to_fix:
            self.fix_file_syntax_errors(file_path)
            self.files_processed += 1

    def run_comprehensive_fix(self):
        """运行综合修复"""
        logger.info("开始微服务语法错误综合修复...")

        # 1. 加载已知错误
        known_errors = self.load_known_errors()
        logger.info(f"发现 {len(known_errors)} 个已知语法错误")

        # 2. 修复已知错误
        if known_errors:
            self.fix_known_errors(known_errors)

        logger.info(
            f"修复完成! 处理了 {self.files_processed} 个文件，修复了 {self.errors_fixed} 个错误"
        )


def main():
    parser = argparse.ArgumentParser(description="索克生活微服务语法错误修复工具")
    parser.add_argument("--project-root", default=".", help="项目根目录路径")

    args = parser.parse_args()

    fixer = MicroserviceSyntaxFixer(args.project_root)
    fixer.run_comprehensive_fix()


if __name__ == "__main__":
    main()
