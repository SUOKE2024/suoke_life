"""
fix_pydantic_env - 索克生活项目模块
"""

from pathlib import Path
import os
import re

#!/usr/bin/env python3
"""
批量修复 Pydantic Field env 参数警告的脚本
"""


def fix_field_env_warnings(file_path):
    """修复单个文件中的 Field env 参数警告"""
    print(f"修复文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 修复 Field(..., env="...", ...) 为 Field(..., json_schema_extra={"env": "..."}, ...)
    def replace_env_param(match):
        before_env = match.group(1)
        env_value = match.group(2)
        after_env = match.group(3)
        
        # 检查是否已经有 json_schema_extra
        if 'json_schema_extra' in before_env or 'json_schema_extra' in after_env:
            return match.group(0)  # 不修改，避免重复
        
        # 构建新的 Field 调用
        if after_env.strip():
            # 有其他参数在 env 之后
            new_field = f'{before_env}json_schema_extra={{"env": "{env_value}"}}, {after_env}'
        else:
            # env 是最后一个参数
            new_field = f'{before_env}json_schema_extra={{"env": "{env_value}"}}{after_env}'
        
        return new_field
    
    # 匹配 Field(..., env="VALUE", ...)
    pattern = r'(Field\([^)]*?)env="([^"]*)"([^)]*?\))'
    content = re.sub(pattern, replace_env_param, content)
    
    # 如果内容有变化，写回文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ 已修复 {file_path}")
        return True
    else:
        print(f"  ⏭️  {file_path} 无需修复")
        return False

def main():
    """主函数"""
    print("🔧 开始修复 Pydantic Field env 参数警告...")
    
    # 查找所有需要修复的 Python 文件
    config_dir = Path("accessibility_service/config")
    
    if not config_dir.exists():
        print(f"❌ 目录不存在: {config_dir}")
        return
    
    python_files = list(config_dir.glob("*.py"))
    
    if not python_files:
        print(f"❌ 在 {config_dir} 中没有找到 Python 文件")
        return
    
    print(f"📁 找到 {len(python_files)} 个配置文件")
    
    fixed_count = 0
    for file_path in python_files:
        if fix_field_env_warnings(file_path):
            fixed_count += 1
    
    print(f"\n✅ 修复完成！共修复了 {fixed_count} 个文件")

if __name__ == "__main__":
    main() 