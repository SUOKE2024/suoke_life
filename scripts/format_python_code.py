#!/usr/bin/env python
"""
格式化索克生活项目中的所有Python文件
使用Black和isort进行代码格式化
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command):
    """运行命令并打印输出"""
    print(f"执行命令: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode


def format_python_file(file_path, check_only=False):
    """格式化单个Python文件"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return 1
    
    # 使用isort格式化导入
    isort_cmd = ["isort"]
    if check_only:
        isort_cmd.append("--check")
    isort_cmd.append(file_path)
    
    isort_result = run_command(isort_cmd)
    if isort_result != 0:
        print("isort格式化失败")
        if check_only:
            return isort_result
    
    # 使用black格式化代码
    black_cmd = ["black"]
    if check_only:
        black_cmd.append("--check")
    black_cmd.append(file_path)
    
    black_result = run_command(black_cmd)
    if black_result != 0:
        print("black格式化失败")
        return black_result
    
    print(f"文件 {file_path} 格式化完成！")
    return 0


def format_python_files(directory, check_only=False):
    """格式化指定目录下的所有Python文件"""
    directory_path = Path(directory)
    
    # 如果是单个文件，直接格式化
    if os.path.isfile(directory) and directory.endswith('.py'):
        return format_python_file(directory, check_only)
    
    # 获取所有Python文件
    python_files = list(directory_path.glob("**/*.py"))
    print(f"找到 {len(python_files)} 个Python文件")
    
    # 排除不需要格式化的目录
    excluded_dirs = [".git", "venv", ".venv", "node_modules", "__pycache__", "migrations"]
    filtered_files = [
        str(f) for f in python_files 
        if not any(excluded in str(f) for excluded in excluded_dirs)
    ]
    
    print(f"将格式化 {len(filtered_files)} 个Python文件")
    
    if not filtered_files:
        print("没有找到需要格式化的文件")
        return 0
    
    # 使用isort格式化导入
    isort_cmd = ["isort"]
    if check_only:
        isort_cmd.append("--check")
    isort_cmd.extend(filtered_files)
    
    isort_result = run_command(isort_cmd)
    if isort_result != 0:
        print("isort格式化失败")
        if check_only:
            return isort_result
    
    # 使用black格式化代码
    black_cmd = ["black"]
    if check_only:
        black_cmd.append("--check")
    black_cmd.extend(filtered_files)
    
    black_result = run_command(black_cmd)
    if black_result != 0:
        print("black格式化失败")
        return black_result
    
    print("格式化完成！")
    return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="格式化Python代码")
    parser.add_argument("--check", action="store_true", help="只检查不修改")
    parser.add_argument("--dir", default=".", help="要格式化的目录或文件，默认为当前目录")
    
    args = parser.parse_args()
    
    sys.exit(format_python_files(args.dir, args.check)) 