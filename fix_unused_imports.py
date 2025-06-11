#!/usr/bin/env python3
"""
修复未使用导入的脚本

自动移除Python文件中未使用的导入语句
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Set, Dict


def get_unused_imports(file_path: str) -> List[Dict[str, str]]:
    """获取文件中未使用的导入"""
    try:
        result = subprocess.run(
            ["ruff", "check", file_path, "--select=F401", "--output-format=json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            import json
            errors = json.loads(result.stdout)
            return [
                {
                    "file": error["filename"],
                    "line": error["location"]["row"],
                    "column": error["location"]["column"],
                    "message": error["message"],
                    "code": error["code"]
                }
                for error in errors
                if error["code"] == "F401"
            ]
    except Exception as e:
        print(f"检查文件 {file_path} 时出错: {e}")
    
    return []


def fix_unused_imports_in_file(file_path: str) -> bool:
    """修复单个文件中的未使用导入"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        
        # 获取未使用的导入
        unused_imports = get_unused_imports(file_path)
        if not unused_imports:
            return False
        
        # 按行号倒序排序，避免删除时行号变化
        unused_imports.sort(key=lambda x: x["line"], reverse=True)
        
        modified = False
        for import_info in unused_imports:
            line_num = import_info["line"] - 1  # 转换为0索引
            if line_num < len(lines):
                line = lines[line_num]
                
                # 提取未使用的导入名称
                message = import_info["message"]
                if "`" in message:
                    import_name = message.split("`")[1]
                    
                    # 处理from typing import语句
                    if line.strip().startswith("from typing import"):
                        # 移除特定的导入
                        imports = line.split("import")[1].strip()
                        import_list = [imp.strip() for imp in imports.split(",")]
                        import_list = [imp for imp in import_list if imp != import_name]
                        
                        if import_list:
                            lines[line_num] = f"from typing import {', '.join(import_list)}"
                        else:
                            lines[line_num] = ""  # 删除整行
                        modified = True
                    
                    # 处理单独的import语句
                    elif line.strip().startswith(f"import {import_name}"):
                        lines[line_num] = ""
                        modified = True
                    
                    # 处理from ... import语句
                    elif f"import {import_name}" in line:
                        if "," in line:
                            # 多个导入，只移除特定的
                            parts = line.split("import")
                            if len(parts) == 2:
                                prefix = parts[0] + "import"
                                imports = parts[1].strip()
                                import_list = [imp.strip() for imp in imports.split(",")]
                                import_list = [imp for imp in import_list if imp != import_name]
                                
                                if import_list:
                                    lines[line_num] = f"{prefix} {', '.join(import_list)}"
                                else:
                                    lines[line_num] = ""
                        else:
                            # 单个导入，删除整行
                            lines[line_num] = ""
                        modified = True
        
        if modified:
            # 清理空行
            cleaned_lines = []
            for i, line in enumerate(lines):
                if line.strip() == "" and i > 0 and i < len(lines) - 1:
                    # 保留必要的空行，移除多余的空行
                    if not (cleaned_lines and cleaned_lines[-1].strip() == ""):
                        cleaned_lines.append(line)
                else:
                    cleaned_lines.append(line)
            
            new_content = '\n'.join(cleaned_lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 修复文件: {file_path}")
            return True
    
    except Exception as e:
        print(f"❌ 修复文件 {file_path} 时出错: {e}")
    
    return False


def fix_unused_imports_in_directory(directory: str) -> int:
    """修复目录中所有Python文件的未使用导入"""
    fixed_count = 0
    
    for root, dirs, files in os.walk(directory):
        # 跳过一些目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_unused_imports_in_file(file_path):
                    fixed_count += 1
    
    return fixed_count


def main():
    """主函数"""
    print("🔧 开始修复未使用的导入...")
    
    current_dir = "."
    fixed_count = fix_unused_imports_in_directory(current_dir)
    
    print(f"\n📊 修复完成:")
    print(f"  修复文件数: {fixed_count}")
    
    # 再次检查
    print("\n🔍 验证修复结果...")
    result = subprocess.run(
        ["ruff", "check", ".", "--select=F401"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ 所有未使用导入已修复!")
    else:
        remaining_errors = result.stdout.count("F401")
        print(f"⚠️ 还有 {remaining_errors} 个未使用导入需要手动处理")


if __name__ == "__main__":
    main() 