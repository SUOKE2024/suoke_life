#!/usr/bin/env python3
"""
批量修复Python语法错误的脚本
"""

import os
import re
import glob

def fix_syntax_errors(file_path):
    """修复单个文件的语法错误"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复各种运算符的空格问题
        content = re.sub(r' \+= ', '+=', content)
        content = re.sub(r' -= ', '-=', content)
        content = re.sub(r' \*= ', '*=', content)
        content = re.sub(r' /= ', '/=', content)
        content = re.sub(r' //= ', '//=', content)
        content = re.sub(r' \*\* ', '**', content)
        content = re.sub(r' >= ', '>=', content)
        content = re.sub(r' <= ', '<=', content)
        content = re.sub(r' != ', '!=', content)
        content = re.sub(r' == ', '==', content)
        content = re.sub(r' // ', '//', content)
        content = re.sub(r' - > ', ' -> ', content)
        content = re.sub(r'1e - (\d+)', r'1e-\1', content)
        content = re.sub(r'(\d+)e - (\d+)', r'\1e-\2', content)
        
        # 修复特殊的语法错误
        content = re.sub(r'>=== ', '>=', content)  # 修复三个等号的问题
        
        # 只有内容发生变化时才写入文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"修复了文件: {file_path}")
            return True
        return False
        
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return False

def main():
    """主函数"""
    # 查找所有Python文件
    python_files = []
    
    # 在services目录下查找
    for root, dirs, files in os.walk('services'):
        # 跳过虚拟环境目录
        dirs[:] = [d for d in dirs if d not in ['.venv', 'venv', '__pycache__']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"找到 {len(python_files)} 个Python文件")
    
    fixed_count = 0
    for file_path in python_files:
        if fix_syntax_errors(file_path):
            fixed_count += 1
    
    print(f"修复了 {fixed_count} 个文件")

if __name__ == "__main__":
    main() 