#!/usr/bin/env python3
"""
批量修复 Pydantic v2 弃用语法的脚本
"""

import os
import re
from pathlib import Path

def fix_pydantic_file(file_path):
    """修复单个文件中的 Pydantic 弃用语法"""
    print(f"修复文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. 修复导入语句
    content = re.sub(
        r'from pydantic import ([^,\n]*?)validator([^,\n]*?)',
        r'from pydantic import \1field_validator\2',
        content
    )
    
    # 2. 修复 @validator 装饰器
    content = re.sub(
        r'@validator\(',
        r'@field_validator(',
        content
    )
    
    # 3. 修复验证器函数定义，添加 @classmethod
    def fix_validator_function(match):
        decorator = match.group(1)
        function_def = match.group(2)
        
        # 如果已经有 @classmethod，就不添加
        if '@classmethod' in decorator:
            return match.group(0)
        
        # 添加 @classmethod
        return f"{decorator}    @classmethod\n{function_def}"
    
    content = re.sub(
        r'(@field_validator\([^)]+\)\n)(    def \w+\(cls, v[^)]*\):)',
        fix_validator_function,
        content,
        flags=re.MULTILINE
    )
    
    # 4. 修复 values 参数为 info
    content = re.sub(
        r'def (\w+)\(cls, v, values\):',
        r'def \1(cls, v, info):',
        content
    )
    
    # 5. 修复 values 使用为 info.data
    content = re.sub(
        r"'([^']+)' in values and values\['([^']+)'\]",
        r"info.data and '\1' in info.data and info.data['\2']",
        content
    )
    
    content = re.sub(
        r"values\['([^']+)'\]",
        r"info.data['\1']",
        content
    )
    
    # 6. 修复 class Config 为 model_config
    content = re.sub(
        r'class Config:\s*\n((?:        [^\n]+\n)*)',
        lambda m: f"model_config = {{\n{convert_config_to_dict(m.group(1))}    }}",
        content,
        flags=re.MULTILINE
    )
    
    # 7. 修复 check_fields=False 参数
    content = re.sub(
        r'@field_validator\(([^)]+), check_fields=False\)',
        r'@field_validator(\1)',
        content
    )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ 已修复")
        return True
    else:
        print(f"  ⏭️  无需修复")
        return False

def convert_config_to_dict(config_content):
    """将 class Config 内容转换为字典格式"""
    lines = config_content.strip().split('\n')
    dict_lines = []
    
    for line in lines:
        line = line.strip()
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            dict_lines.append(f'        "{key}": {value},')
    
    return '\n'.join(dict_lines) + '\n'

def main():
    """主函数"""
    print("🔧 开始修复 Pydantic v2 弃用语法...")
    
    # 需要修复的文件列表
    files_to_fix = [
        "accessibility_service/config/logging.py",
        "accessibility_service/config/database.py", 
        "accessibility_service/config/redis.py",
        "accessibility_service/models/user.py",
        "accessibility_service/models/analysis.py"
    ]
    
    fixed_count = 0
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_pydantic_file(file_path):
                fixed_count += 1
        else:
            print(f"⚠️  文件不存在: {file_path}")
    
    print(f"\n✅ 修复完成！共修复了 {fixed_count} 个文件")

if __name__ == "__main__":
    main() 