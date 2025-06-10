#!/usr/bin/env python3
"""
修复统一健康数据服务的语法错误
"""

import re
from pathlib import Path


def fix_arrow_syntax(content: str) -> str:
    """修复箭头函数语法"""
    # 修复 - > 为 ->
    content = re.sub(r'\s*-\s*>\s*', ' -> ', content)
    return content


def fix_division_syntax(content: str) -> str:
    """修复除法语法"""
    # 修复 / / 为 //
    content = re.sub(r'\s*/\s*/\s*', ' // ', content)
    return content


def fix_kwargs_syntax(content: str) -> str:
    """修复**kwargs语法"""
    # 修复 * *kwargs 为 **kwargs
    content = re.sub(r'\*\s*\*(\w+)', r'**\1', content)
    return content


def fix_import_syntax(content: str) -> str:
    """修复导入语法错误"""
    lines = content.split('\n')
    fixed_lines = []
    in_import = False
    import_buffer = []
    
    for line in lines:
        stripped = line.strip()
        
        # 检查是否是未闭合的导入语句
        if ('from ' in stripped and 'import (' in stripped and 
            not stripped.endswith(')')):
            in_import = True
            import_buffer = [line]
        elif in_import:
            import_buffer.append(line)
            if ')' in line:
                # 重构导入语句为简单形式
                import_text = ' '.join(import_buffer)
                module_match = re.search(r'from\s+([^\s]+)\s+import\s+\(', import_text)
                if module_match:
                    module = module_match.group(1)
                    # 根据模块类型添加常见导入
                    if 'data_standardization' in module:
                        fixed_lines.append(f'from {module} import DataStandardizer, QualityChecker')
                    elif 'zk_snarks' in module:
                        fixed_lines.append(f'from {module} import ProofSystem, VerificationKey')
                    else:
                        fixed_lines.append(f'from {module} import *')
                in_import = False
                import_buffer = []
        else:
            if not in_import:
                fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_indentation(content: str) -> str:
    """修复缩进问题"""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        if line.strip():
            # 检查是否是错误的缩进
            if line.startswith('        ') and i > 0:
                # 8个空格缩进，检查上下文
                prev_line = lines[i-1].strip() if i > 0 else ''
                if (prev_line.startswith('import ') or 
                    prev_line.startswith('from ') or
                    not prev_line.endswith(':')):
                    # 移除多余缩进
                    fixed_lines.append(line.lstrip())
                else:
                    # 保持4个空格缩进
                    fixed_lines.append('    ' + line.lstrip())
            elif line.startswith('    ') and i > 0:
                # 4个空格缩进，检查是否合理
                prev_line = lines[i-1].strip() if i > 0 else ''
                if (prev_line.startswith('import ') or 
                    prev_line.startswith('from ') or
                    prev_line.startswith('def ') or
                    prev_line.startswith('class ') or
                    prev_line.startswith('@')):
                    # 移除缩进
                    fixed_lines.append(line.lstrip())
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append('')
    
    return '\n'.join(fixed_lines)


def fix_typing_imports(content: str) -> str:
    """修复typing导入"""
    # 移除未使用的typing导入
    content = re.sub(r'from typing import Dict, List, Any, Optional, Union\n', '', content)
    content = re.sub(r'from typing import .*Dict.*\n', '', content)
    content = re.sub(r'from typing import .*List.*\n', '', content)
    
    # 替换类型注解
    content = re.sub(r'\bDict\b', 'dict', content)
    content = re.sub(r'\bList\b', 'list', content)
    return content


def fix_bare_except(content: str) -> str:
    """修复bare except"""
    content = re.sub(r'except:', 'except Exception:', content)
    return content


def fix_source_file(file_path: Path):
    """修复单个源文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 应用各种修复
        content = fix_arrow_syntax(content)
        content = fix_division_syntax(content)
        content = fix_kwargs_syntax(content)
        content = fix_import_syntax(content)
        content = fix_typing_imports(content)
        content = fix_indentation(content)
        content = fix_bare_except(content)
        
        # 确保文件以换行符结尾
        if not content.endswith('\n'):
            content += '\n'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed {file_path}")
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")


def main():
    """主函数"""
    source_dir = Path('unified_health_data_service')
    
    # 遍历所有Python源文件
    for py_file in source_dir.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
        
        print(f"Processing {py_file}")
        fix_source_file(py_file)
    
    print("All source files fixed!")


if __name__ == "__main__":
    main() 