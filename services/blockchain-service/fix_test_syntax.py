#!/usr/bin/env python3
"""
修复区块链服务测试文件的语法错误
"""

from pathlib import Path
import re


def fix_arrow_syntax(content: str) -> str:
    """修复箭头函数语法"""
    # 修复 -> 为 ->
    content = re.sub(r"\s*-\s*>\s*", " -> ", content)
    return content


def fix_indentation(content: str) -> str:
    """修复缩进问题"""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        # 移除行首的多余空格，保持正确的缩进
        if line.strip():
            # 计算应该的缩进级别
            stripped = line.lstrip()
            if stripped.startswith(("import ", "from ")):
                # 导入语句不应该有缩进
                fixed_lines.append(stripped)
            elif stripped.startswith(("def ", "class ", "@")):
                # 函数、类、装饰器不应该有缩进（除非在类内部）
                fixed_lines.append(stripped)
            elif stripped.startswith(("if ", "elif ", "else:", "for ", "while ", "try:", "except", "finally:")):
                # 控制流语句
                fixed_lines.append(stripped)
            # 其他语句，保持适当缩进
            elif any(fixed_lines) and fixed_lines[-1].strip().endswith(":"):
                # 如果上一行以冒号结尾，这行应该缩进
                fixed_lines.append("    " + stripped)
            else:
                fixed_lines.append(stripped)
        else:
            fixed_lines.append("")

    return "\n".join(fixed_lines)


def fix_import_syntax(content: str) -> str:
    """修复导入语法错误"""
    # 修复未闭合的括号
    content = re.sub(r"from\s+([^\\n]+)\s+import\s+\(\s*$", r"from \1 import (", content, flags=re.MULTILINE)

    # 修复多行导入
    lines = content.split("\n")
    fixed_lines = []
    in_import = False
    import_buffer = []

    for line in lines:
        if "import (" in line and not line.strip().endswith(")"):
            in_import = True
            import_buffer = [line]
        elif in_import:
            import_buffer.append(line)
            if ")" in line:
                # 重构导入语句
                import_text = " ".join(import_buffer)
                # 简化为单行导入
                module_match = re.search(r"from\s+([^\s]+)\s+import\s+\(", import_text)
                if module_match:
                    module = module_match.group(1)
                    fixed_lines.append(f"from {module} import ValidationError, NotFoundError, BlockchainServiceError")
                in_import = False
                import_buffer = []
        elif not in_import:
            fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_typing_imports(content: str) -> str:
    """修复typing导入"""
    content = re.sub(r"from typing import ([^\\n]*,\\s*)*Dict([^\\n]*,\\s*)*",
                    lambda m: m.group(0).replace("Dict", "dict"), content)
    content = re.sub(r"from typing import ([^\\n]*,\\s*)*List([^\\n]*,\\s*)*",
                    lambda m: m.group(0).replace("List", "list"), content)
    return content


def fix_test_file(file_path: Path):
    """修复单个测试文件"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # 应用各种修复
        content = fix_arrow_syntax(content)
        content = fix_import_syntax(content)
        content = fix_typing_imports(content)
        content = fix_indentation(content)

        # 确保文件以换行符结尾
        if not content.endswith("\n"):
            content += "\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Fixed {file_path}")

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")


def main():
    """主函数"""
    tests_dir = Path("tests")

    # 遍历所有Python测试文件
    for py_file in tests_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        print(f"Processing {py_file}")
        fix_test_file(py_file)

    print("All test files fixed!")


if __name__ == "__main__":
    main()
