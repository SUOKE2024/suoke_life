#!/usr/bin/env python3
"""
修复统一健康数据服务的缩进和语法错误
"""

import re
from pathlib import Path

def fix_indentation_errors():
    """修复缩进错误"""
    
    # 需要修复的文件
    files_to_fix = [
        "unified_health_data_service/health_data_service/utils/processors.py",
        "unified_health_data_service/health_data_service/utils/validators.py"
    ]
    
    for file_path in files_to_fix:
        if not Path(file_path).exists():
            print(f"文件不存在: {file_path}")
            continue
            
        print(f"修复文件: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复常见的缩进问题
        lines = content.split('\n')
        fixed_lines = []
        in_function = False
        in_class = False
        in_try_block = False
        expected_indent = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 跳过空行
            if not stripped:
                fixed_lines.append('')
                continue
            
            # 检测类定义
            if stripped.startswith('class '):
                in_class = True
                expected_indent = 0
                fixed_lines.append(line)
                continue
            
            # 检测函数定义
            if stripped.startswith('def ') or stripped.startswith('async def '):
                in_function = True
                if in_class:
                    expected_indent = 4
                else:
                    expected_indent = 0
                fixed_lines.append(' ' * expected_indent + stripped)
                continue
            
            # 检测文档字符串
            if stripped.startswith('"""') and stripped.endswith('"""') and len(stripped) > 6:
                if in_function:
                    fixed_lines.append(' ' * (expected_indent + 4) + stripped)
                else:
                    fixed_lines.append(' ' * expected_indent + stripped)
                continue
            
            # 检测try块
            if stripped.startswith('try:'):
                in_try_block = True
                if in_function:
                    fixed_lines.append(' ' * (expected_indent + 4) + stripped)
                else:
                    fixed_lines.append(' ' * expected_indent + stripped)
                continue
            
            # 检测except块
            if stripped.startswith('except '):
                if in_function:
                    fixed_lines.append(' ' * (expected_indent + 4) + stripped)
                else:
                    fixed_lines.append(' ' * expected_indent + stripped)
                continue
            
            # 检测return语句
            if stripped.startswith('return '):
                if in_try_block:
                    if in_function:
                        fixed_lines.append(' ' * (expected_indent + 8) + stripped)
                    else:
                        fixed_lines.append(' ' * (expected_indent + 4) + stripped)
                elif in_function:
                    fixed_lines.append(' ' * (expected_indent + 4) + stripped)
                else:
                    fixed_lines.append(' ' * expected_indent + stripped)
                continue
            
            # 检测raise语句
            if stripped.startswith('raise '):
                if in_try_block:
                    if in_function:
                        fixed_lines.append(' ' * (expected_indent + 8) + stripped)
                    else:
                        fixed_lines.append(' ' * (expected_indent + 4) + stripped)
                elif in_function:
                    fixed_lines.append(' ' * (expected_indent + 4) + stripped)
                else:
                    fixed_lines.append(' ' * expected_indent + stripped)
                continue
            
            # 检测if/elif/else语句
            if stripped.startswith(('if ', 'elif ', 'else:')):
                if in_function:
                    fixed_lines.append(' ' * (expected_indent + 4) + stripped)
                else:
                    fixed_lines.append(' ' * expected_indent + stripped)
                continue
            
            # 检测for/while循环
            if stripped.startswith(('for ', 'while ')):
                if in_function:
                    fixed_lines.append(' ' * (expected_indent + 4) + stripped)
                else:
                    fixed_lines.append(' ' * expected_indent + stripped)
                continue
            
            # 普通代码行
            if in_function:
                # 检查是否是函数体内的代码
                if stripped and not stripped.startswith('#'):
                    fixed_lines.append(' ' * (expected_indent + 4) + stripped)
                else:
                    fixed_lines.append(' ' * (expected_indent + 4) + stripped)
            else:
                fixed_lines.append(stripped)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        
        print(f"已修复: {file_path}")

def fix_specific_syntax_errors():
    """修复特定的语法错误"""
    
    files_to_fix = [
        "unified_health_data_service/health_data_service/utils/processors.py",
        "unified_health_data_service/health_data_service/utils/validators.py"
    ]
    
    for file_path in files_to_fix:
        if not Path(file_path).exists():
            continue
            
        print(f"修复语法错误: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复except语法错误
        content = re.sub(r'except \(([^)]+)\):', r'except (\1):', content)
        
        # 修复箭头函数语法
        content = re.sub(r'- >', r'->', content)
        
        # 修复除法语法
        content = re.sub(r'/ /', r'//', content)
        
        # 修复kwargs语法
        content = re.sub(r'\*\* kwargs', r'**kwargs', content)
        
        # 修复全角字符
        content = content.replace('，', ',')
        content = content.replace('。', '.')
        content = content.replace('：', ':')
        content = content.replace('；', ';')
        content = content.replace('"', '"')
        content = content.replace('"', '"')
        content = content.replace(''', "'")
        content = content.replace(''', "'")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已修复语法错误: {file_path}")

if __name__ == "__main__":
    print("开始修复缩进和语法错误...")
    fix_specific_syntax_errors()
    fix_indentation_errors()
    print("修复完成!") 