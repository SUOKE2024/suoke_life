#!/usr/bin/env python3
"""
批量修复参数名问题的脚本
"""

import re
import glob

def fix_parameter_names(file_path):
    """修复文件中的参数名问题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复常见的参数名模式
        patterns = [
            (r'_([a-zA-Z_][a-zA-Z0-9_]*): ([a-zA-Z_][a-zA-Z0-9_\[\]|. ]*)', r'\1: \2'),
            (r'_([a-zA-Z_][a-zA-Z0-9_]*) =', r'\1 ='),
            (r'_([a-zA-Z_][a-zA-Z0-9_]*)\)', r'\1)'),
            (r'_([a-zA-Z_][a-zA-Z0-9_]*),', r'\1,'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # 如果内容有变化，写回文件
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
    # 获取所有Python文件
    python_files = glob.glob('xiaoai/**/*.py', recursive=True)
    
    fixed_count = 0
    for file_path in python_files:
        if fix_parameter_names(file_path):
            fixed_count += 1
    
    print(f"总共修复了 {fixed_count} 个文件")

if __name__ == '__main__':
    main() 