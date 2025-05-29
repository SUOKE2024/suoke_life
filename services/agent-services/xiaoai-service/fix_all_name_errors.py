#!/usr/bin/env python3
"""
批量修复 xiaoai-service 中的所有 __name__ 相关错误
包括 _name__, ___name__, ____name__ 等
"""

import os
import re
from pathlib import Path

def fix_name_errors(directory: str):
    """修复目录中所有 Python 文件的 __name__ 相关错误"""
    fixed_files = []
    error_files = []
    
    # 定义需要修复的模式 - 使用更强的正则表达式
    patterns = [
        # 匹配任意数量的下划线 + name + 两个下划线
        (r'_{1,10}name__', '__name__'),
        # 特别处理 logging.getLogger 的情况
        (r'logging\.getLogger\(_{1,10}name__\)', 'logging.getLogger(__name__)'),
        # 处理字符串格式化中的情况
        (r'f"[^"]*\{_{1,10}name__\}[^"]*"', lambda m: m.group(0).replace('_name__', '__name__').replace('___name__', '__name__').replace('____name__', '__name__')),
    ]
    
    # 查找所有 Python 文件
    for root, dirs, files in os.walk(directory):
        # 跳过虚拟环境和缓存目录
        dirs[:] = [d for d in dirs if d not in ['.venv', '__pycache__', '.ruff_cache', '.mypy_cache']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # 简单的字符串替换方法
                    replacements = [
                        ('_name__', '__name__'),
                        ('___name__', '__name__'),
                        ('____name__', '__name__'),
                        ('_____name__', '__name__'),
                        ('______name__', '__name__'),
                    ]
                    
                    for old, new in replacements:
                        content = content.replace(old, new)
                    
                    # 如果内容有变化，写回文件
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        fixed_files.append(file_path)
                        print(f"✅ 修复: {file_path}")
                
                except Exception as e:
                    error_files.append((file_path, str(e)))
                    print(f"❌ 错误: {file_path} - {e}")
    
    return fixed_files, error_files

def main():
    """主函数"""
    print("开始修复 xiaoai-service 中的所有 __name__ 相关错误...")
    
    # 当前目录应该是 xiaoai-service 根目录
    xiaoai_dir = "./xiaoai"
    
    if not os.path.exists(xiaoai_dir):
        print(f"❌ 错误: 找不到 xiaoai 目录: {xiaoai_dir}")
        return
    
    fixed_files, error_files = fix_name_errors(xiaoai_dir)
    
    print(f"\n修复完成!")
    print(f"✅ 成功修复文件数: {len(fixed_files)}")
    print(f"❌ 错误文件数: {len(error_files)}")
    
    if error_files:
        print("\n错误文件列表:")
        for file_path, error in error_files:
            print(f"  - {file_path}: {error}")

if __name__ == "__main__":
    main() 