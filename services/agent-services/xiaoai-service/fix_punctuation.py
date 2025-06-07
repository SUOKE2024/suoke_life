#!/usr/bin/env python3
"""修复中文标点符号问题"""

import re
import os
from pathlib import Path

def fix_chinese_punctuation(file_path):
    """修复文件中的中文标点符号"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复中文标点符号
        replacements = {
            '，': ',',  # 全角逗号 -> 半角逗号
            '。': '.',  # 全角句号 -> 半角句号
            '：': ':',  # 全角冒号 -> 半角冒号
            '；': ';',  # 全角分号 -> 半角分号
            '（': '(',  # 全角左括号 -> 半角左括号
            '）': ')',  # 全角右括号 -> 半角右括号
            '！': '!',  # 全角感叹号 -> 半角感叹号
            '？': '?',  # 全角问号 -> 半角问号
        }
        
        # 只在字符串和注释中替换，避免影响中文文本内容
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 如果是注释行或包含字符串的代码行，进行替换
            if line.strip().startswith('#') or '"' in line or "'" in line:
                for old, new in replacements.items():
                    line = line.replace(old, new)
            fixed_lines.append(line)
        
        new_content = '\n'.join(fixed_lines)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'Fixed: {file_path}')
            return True
    except Exception as e:
        print(f'Error fixing {file_path}: {e}')
    return False

def main():
    """主函数"""
    # 修复所有Python文件
    xiaoai_dir = Path('xiaoai')
    fixed_count = 0

    for py_file in xiaoai_dir.rglob('*.py'):
        if fix_chinese_punctuation(py_file):
            fixed_count += 1

    print(f'Total files fixed: {fixed_count}')

if __name__ == "__main__":
    main() 