#!/usr/bin/env python3
"""
修复xiaoai-service剩余的代码问题
"""

import re
from pathlib import Path


def fix_typing_imports(file_path: Path):
    """修复typing导入问题"""
    try:
        with file_path.open(encoding='utf-8') as f:
            content = f.read()

        # 替换过时的typing导入
        content = re.sub(r'from typing import ([^,\n]*,\s*)*dict([^,\n]*,\s*)*',
                        lambda m: m.group(0).replace('dict', 'dict'), content)
        content = re.sub(r'from typing import ([^,\n]*,\s*)*list([^,\n]*,\s*)*',
                        lambda m: m.group(0).replace('list', 'list'), content)

        # 替换类型注解中的dict和list
        content = re.sub(r'\bdict\[', 'dict[', content)
        content = re.sub(r'\blist\[', 'list[', content)

        with file_path.open('w', encoding='utf-8') as f:
            f.write(content)

        print(f"Fixed typing imports in {file_path}")

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")


def fix_unicode_issues(file_path: Path):
    """修复Unicode字符问题"""
    try:
        with file_path.open(encoding='utf-8') as f:
            content = f.read()

        # 替换全角逗号为半角逗号
        content = content.replace('\uff0c', ',')  # 全角逗号
        # 替换全角句号为半角句号
        content = content.replace('\u3002', '.')  # 全角句号
        # 替换全角分号为半角分号
        content = content.replace('\uff1b', ';')  # 全角分号
        # 替换全角冒号为半角冒号
        content = content.replace('\uff1a', ':')  # 全角冒号

        with file_path.open('w', encoding='utf-8') as f:
            f.write(content)

        print(f"Fixed unicode issues in {file_path}")

    except Exception as e:
        print(f"Error fixing unicode in {file_path}: {e}")


def fix_import_order(file_path: Path):
    """修复导入顺序问题"""
    try:
        with file_path.open(encoding='utf-8') as f:
            lines = f.readlines()

        # 找到文档字符串结束位置
        docstring_end = 0
        quote_count = 0

        for i, line in enumerate(lines):
            if '"""' in line:
                quote_count += line.count('"""')
                if quote_count >= 2:
                    docstring_end = i + 1
                    break

        # 将导入语句移到文档字符串后面
        imports = []
        other_lines = []

        for i, line in enumerate(lines):
            if i < docstring_end:
                other_lines.append(line)
            elif line.strip().startswith(('from ', 'import ')):
                imports.append(line)
            else:
                other_lines.append(line)

        # 重新组织文件内容
        if imports:
            new_content = other_lines[:docstring_end] + ['\n'] + imports + ['\n'] + other_lines[docstring_end:]

            with file_path.open('w', encoding='utf-8') as f:
                f.writelines(new_content)

            print(f"Fixed import order in {file_path}")

    except Exception as e:
        print(f"Error fixing import order in {file_path}: {e}")


def main():
    """主函数"""
    current_dir = Path()

    # 遍历所有Python文件
    for py_file in current_dir.rglob('*.py'):
        if '.venv' in str(py_file) or '__pycache__' in str(py_file):
            continue

        print(f"Processing {py_file}")

        # 修复typing导入
        fix_typing_imports(py_file)

        # 修复Unicode问题
        fix_unicode_issues(py_file)

        # 修复导入顺序
        fix_import_order(py_file)

    print("All fixes completed!")


if __name__ == "__main__":
    main()
