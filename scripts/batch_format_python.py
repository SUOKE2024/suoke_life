#!/usr/bin/env python
"""
批量格式化索克生活项目中的Python文件
将文件分批处理，避免一次处理过多文件导致的问题
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def find_python_files(directory):
    """查找指定目录下的所有Python文件"""
    directory_path = Path(directory)

    # 获取所有Python文件
    python_files = list(directory_path.glob("**/*.py"))

    # 排除不需要格式化的目录
    excluded_dirs = [
        ".git",
        "venv",
        ".venv",
        "node_modules",
        "__pycache__",
        "migrations",
    ]
    filtered_files = [
        str(f)
        for f in python_files
        if not any(excluded in str(f) for excluded in excluded_dirs)
    ]

    return filtered_files


def format_file_batch(file_batch):
    """格式化一批文件"""
    if not file_batch:
        return 0

    # 使用isort格式化导入
    isort_cmd = ["isort"] + file_batch
    subprocess.run(isort_cmd, capture_output=True, text=True)

    # 使用black格式化代码
    black_cmd = ["black"] + file_batch
    subprocess.run(black_cmd, capture_output=True, text=True)

    return len(file_batch)


def batch_format_files(directory, batch_size=50, delay=1):
    """分批格式化文件"""
    all_files = find_python_files(directory)
    total_files = len(all_files)

    print(f"找到 {total_files} 个Python文件，将分批格式化")

    processed_count = 0
    batch_count = 0

    # 分批处理文件
    for i in range(0, total_files, batch_size):
        batch_count += 1
        file_batch = all_files[i : i + batch_size]
        print(f"正在处理第 {batch_count} 批，共 {len(file_batch)} 个文件")

        try:
            processed = format_file_batch(file_batch)
            processed_count += processed
            print(f"已处理 {processed_count}/{total_files} 个文件")

            # 添加延迟，避免过快处理
            if i + batch_size < total_files:
                print(f"等待 {delay} 秒后继续...")
                time.sleep(delay)

        except Exception as e:
            print(f"处理批次 {batch_count} 时出错: {e}")

    print(f"格式化完成！共处理 {processed_count}/{total_files} 个文件")
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="批量格式化Python代码")
    parser.add_argument("--dir", default=".", help="要格式化的目录，默认为当前目录")
    parser.add_argument(
        "--batch-size", type=int, default=50, help="每批处理的文件数量，默认为50"
    )
    parser.add_argument(
        "--delay", type=int, default=1, help="批次间延迟秒数，默认为1秒"
    )

    args = parser.parse_args()

    sys.exit(batch_format_files(args.dir, args.batch_size, args.delay))
