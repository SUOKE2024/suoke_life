#!/usr/bin/env python3
"""
修复区块链服务源代码的语法错误
"""

from pathlib import Path
import re


def fix_syntax_errors(file_path):
    """修复单个文件的语法错误"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # 修复箭头函数语法 - 更精确的匹配
    content = re.sub(r"def\s+([^(]+)\([^)]*\)\s*-\s*>\s*([^:]+):", r"def \1() -> \2:", content)
    content = re.sub(r"async\s+def\s+([^(]+)\([^)]*\)\s*-\s*>\s*([^:]+):", r"async def \1() -> \2:", content)

    # 修复简单的箭头语法
    content = re.sub(r"->", r"->", content)
    content = re.sub(r"-  >", r"->", content)
    content = re.sub(r"-   >", r"->", content)

    # 修复除法语法
    content = re.sub(r"//", r"//", content)
    content = re.sub(r"/  /", r"//", content)

    # 修复kwargs语法
    content = re.sub(r"\*\* kwargs", r"**kwargs", content)
    content = re.sub(r"\*\*  kwargs", r"**kwargs", content)

    # 修复全角字符
    content = content.replace("，", ",")
    content = content.replace("。", ".")
    content = content.replace("：", ":")
    content = content.replace("；", ";")
    content = content.replace('"', '"')
    content = content.replace('"', '"')
    content = content.replace(""", "'")
    content = content.replace(""", "'")

    # 修复typing导入
    content = re.sub(r"from typing import Dict, List", r"from typing import dict, list", content)

    return content

def main():
    """主函数"""
    source_dir = Path("suoke_blockchain_service")

    if not source_dir.exists():
        print(f"Source directory {source_dir} not found!")
        return

    # 获取所有Python文件
    python_files = list(source_dir.glob("*.py"))

    for file_path in python_files:
        print(f"Processing {file_path}")

        try:
            fixed_content = fix_syntax_errors(file_path)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)

            print(f"Fixed {file_path}")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print("All source files fixed!")

if __name__ == "__main__":
    main()
