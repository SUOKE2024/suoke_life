#!/usr/bin/env python3
"""
区块链服务深度优化脚本
"""

import os
import re


def fix_typing_imports():
    """修复typing导入问题"""
    print("🔧 修复typing导入...")

    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 修复typing导入
                    content = re.sub(r"from typing import List", content)
                    content = re.sub(r"from typing import Dict", content)
                    content = re.sub(r"List\[", "list[", content)
                    content = re.sub(r"Dict\[", "dict[", content)

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                except Exception as e:
                    print(f"⚠️ 处理文件 {file_path} 时出错: {e}")


def fix_fullwidth_characters():
    """修复全角字符"""
    print("🔧 修复全角字符...")

    replacements = {
        "，": ",",
        "。": ".",
        "：": ":",
        "；": ";",
        "（": "(",
        "）": ")",
        '"': '"',
        '"': '"',
        """: "'",
        """: "'",
    }

    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 只在注释中替换全角字符
                    lines = content.split("\n")
                    fixed_lines = []

                    for line in lines:
                        if "#" in line:
                            # 分离代码和注释
                            code_part, comment_part = line.split("#", 1)
                            # 只在注释部分替换全角字符
                            for old, new in replacements.items():
                                comment_part = comment_part.replace(old, new)
                            line = code_part + "#" + comment_part
                        fixed_lines.append(line)

                    content = "\n".join(fixed_lines)

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                except Exception as e:
                    print(f"⚠️ 处理文件 {file_path} 时出错: {e}")


def fix_indentation_issues():
    """修复缩进问题"""
    print("🔧 修复缩进问题...")

    problematic_files = [
        "blockchain_service/privacy/zkp_manager.py",
        "blockchain_service/enhanced_health_data_manager.py",
        "suoke_blockchain_service/models.py",
    ]

    for file_path in problematic_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # 修复常见的缩进问题
                lines = content.split("\n")
                fixed_lines = []
                in_class = False
                in_function = False

                for i, line in enumerate(lines):
                    stripped = line.strip()

                    # 检测类和函数定义
                    if stripped.startswith("class "):
                        in_class = True
                        in_function = False
                        fixed_lines.append(stripped)
                    elif stripped.startswith("def ") or stripped.startswith(
                        "async def "
                    ):
                        in_function = True
                        if in_class:
                            fixed_lines.append("    " + stripped)
                        else:
                            fixed_lines.append(stripped)
                    elif stripped.startswith("@"):
                        # 装饰器
                        if in_class:
                            fixed_lines.append("    " + stripped)
                        else:
                            fixed_lines.append(stripped)
                    elif stripped == "":
                        # 空行
                        fixed_lines.append("")
                    elif stripped.startswith('"""') or stripped.startswith("'''"):
                        # 文档字符串
                        if in_function and in_class:
                            fixed_lines.append("        " + stripped)
                        elif in_function:
                            fixed_lines.append("    " + stripped)
                        else:
                            fixed_lines.append(stripped)
                    else:
                        # 普通代码行
                        if in_function and in_class:
                            fixed_lines.append("        " + stripped)
                        elif in_function or in_class:
                            fixed_lines.append("    " + stripped)
                        else:
                            fixed_lines.append(stripped)

                    # 重置状态
                    if (
                        stripped
                        and not stripped.startswith(" ")
                        and not stripped.startswith("#")
                    ):
                        if not stripped.startswith(
                            ("class ", "def ", "async def ", "@")
                        ):
                            in_class = False
                            in_function = False

                content = "\n".join(fixed_lines)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"✓ 修复缩进: {file_path}")

            except Exception as e:
                print(f"⚠️ 处理文件 {file_path} 时出错: {e}")


def create_missing_init_files():
    """创建缺失的__init__.py文件"""
    print("🔧 创建缺失的__init__.py文件...")

    directories = []
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if not dir_name.startswith(".") and dir_name != "__pycache__":
                dir_path = os.path.join(root, dir_name)
                init_file = os.path.join(dir_path, "__init__.py")
                if not os.path.exists(init_file):
                    directories.append(dir_path)

    for dir_path in directories:
        init_file = os.path.join(dir_path, "__init__.py")
        with open(init_file, "w", encoding="utf-8") as f:
            f.write('"""模块初始化文件"""\n')
        print(f"✓ 创建: {init_file}")


def optimize_imports():
    """优化导入语句"""
    print("🔧 优化导入语句...")

    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 移除未使用的导入
                    lines = content.split("\n")
                    fixed_lines = []

                    for line in lines:
                        # 跳过明显未使用的导入
                        if line.strip().startswith(
                            "from grpc._utilities import first_version_is_lower"
                        ) and "first_version_is_lower" not in content.replace(line, ""):
                            continue
                        fixed_lines.append(line)

                    content = "\n".join(fixed_lines)

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                except Exception as e:
                    print(f"⚠️ 处理文件 {file_path} 时出错: {e}")


def main():
    """主函数"""
    print("🚀 开始区块链服务深度优化...")

    fix_typing_imports()
    fix_fullwidth_characters()
    fix_indentation_issues()
    create_missing_init_files()
    optimize_imports()

    print("🎉 深度优化完成!")

    # 检查优化效果
    print("\n📊 检查优化效果...")
    os.system("ruff check . | wc -l")


if __name__ == "__main__":
    main()
