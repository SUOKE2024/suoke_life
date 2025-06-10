#!/usr/bin/env python3
"""
全面修复区块链服务的语法错误
"""

from pathlib import Path
import re


def fix_comprehensive_syntax_errors(file_path):
    """修复单个文件的所有语法错误"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # 修复参数语法错误
    content = re.sub(r"\*\s+args", r"*args", content)
    content = re.sub(r"\*\s+\*\s*kwargs", r"**kwargs", content)
    content = re.sub(r"\*\s+\*kwargs", r"**kwargs", content)

    # 修复运算符语法错误
    content = re.sub(r"\+\s*=", r"+=", content)
    content = re.sub(r"-\s*=", r"-=", content)
    content = re.sub(r"\*\s*=", r"*=", content)
    content = re.sub(r"/\s*=", r"/=", content)
    content = re.sub(r">\s*=", r">=", content)
    content = re.sub(r"<\s*=", r"<=", content)
    content = re.sub(r"!\s*=", r"!=", content)
    content = re.sub(r"=\s*=", r"==", content)

    # 修复URL中的空格
    content = re.sub(r"/\s+api\s+/\s+v0\s+/", r"/api/v0/", content)
    content = re.sub(r"/\s+api\s+/", r"/api/", content)

    # 修复函数参数中的空格
    content = re.sub(r'=\s+(["\'])', r"=\1", content)
    content = re.sub(r"total\s*=\s*30", r"total=30", content)
    content = re.sub(r"colors\s*=\s*True", r"colors=True", content)

    return content

def main():
    """主函数"""
    source_dir = Path("suoke_blockchain_service")
    utils_dir = Path("utils")

    # 处理源代码目录
    if source_dir.exists():
        python_files = list(source_dir.glob("*.py"))
        for file_path in python_files:
            print(f"修复源文件: {file_path}")
            try:
                fixed_content = fix_comprehensive_syntax_errors(file_path)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                print(f"已修复: {file_path}")
            except Exception as e:
                print(f"修复失败 {file_path}: {e}")

    # 处理工具目录
    if utils_dir.exists():
        python_files = list(utils_dir.glob("*.py"))
        for file_path in python_files:
            print(f"修复工具文件: {file_path}")
            try:
                fixed_content = fix_comprehensive_syntax_errors(file_path)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                print(f"已修复: {file_path}")
            except Exception as e:
                print(f"修复失败 {file_path}: {e}")

    print("全面语法修复完成!")

if __name__ == "__main__":
    main()
