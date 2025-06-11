#!/usr/bin/env python3
"""
修复Python文件缩进问题的脚本
"""

import os
import re
from pathlib import Path


def fix_file_indentation(file_path: str) -> bool:
    """修复单个文件的缩进问题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        modified = False
        
        for i, line in enumerate(lines):
            original_line = line
            
            # 修复开头的意外缩进
            if line.startswith('    from ') and i == 0:
                # 第一行不应该有缩进
                line = line.lstrip()
                modified = True
            elif line.startswith('                    import '):
                # 过度缩进的import语句
                line = 'import ' + line.split('import ', 1)[1]
                modified = True
            elif line.startswith('    import ') and i == 1:
                # 第二行的import不应该有缩进
                line = line.lstrip()
                modified = True
            
            fixed_lines.append(line)
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            print(f"✅ 修复缩进: {file_path}")
            return True
    
    except Exception as e:
        print(f"❌ 修复文件 {file_path} 时出错: {e}")
    
    return False


def fix_incomplete_imports(file_path: str) -> bool:
    """修复不完整的import语句"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复不完整的import语句
        patterns = [
            (r'from ([^)]+) import \(\s*$', r'# from \1 import ('),  # 注释掉不完整的import
            (r'from ([^)]+) import \(\s*\n', r'# from \1 import (\n'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 修复import: {file_path}")
            return True
    
    except Exception as e:
        print(f"❌ 修复文件 {file_path} 时出错: {e}")
    
    return False


def main():
    """主函数"""
    print("🔧 开始修复缩进和import问题...")
    
    fixed_count = 0
    
    for root, dirs, files in os.walk('.'):
        # 跳过一些目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                if fix_file_indentation(file_path):
                    fixed_count += 1
                
                if fix_incomplete_imports(file_path):
                    fixed_count += 1
    
    print(f"\n📊 修复完成，共修复 {fixed_count} 个问题")


if __name__ == "__main__":
    main() 