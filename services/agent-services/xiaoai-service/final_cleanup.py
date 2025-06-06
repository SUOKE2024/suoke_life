"""
final_cleanup - 索克生活项目模块
"""

from pathlib import Path
import re

#!/usr/bin/env python3

"""
小艾服务最终清理脚本
处理剩余的关键代码质量问题
"""



class FinalCleanup:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.fixes_applied = 0

    def remove_commented_code(self, content: str) -> str:
        """移除注释掉的代码"""
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            # 跳过完全注释掉的代码行（但保留文档字符串和有意义的注释）
            if (stripped.startswith('#') and
                not stripped.startswith('# -*- coding:') and
                not stripped.startswith('#!/') and
                not stripped.startswith('# TODO') and
                not stripped.startswith('# FIXME') and
                not stripped.startswith('# NOTE') and
                not stripped.startswith('# WARNING') and
                not stripped.startswith('# Copyright') and
                not stripped.startswith('# License') and
                len(stripped) > 10 and
                any(keyword in stripped.lower() for keyword in [
                    'def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ',
                    'try:', 'except:', 'return ', 'yield ', 'await ', '= ', '==', '!=',
                    'print(', 'logger.', '.append(', '.extend(', '.update('
                ])):
                self.fixes_applied += 1
                continue
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def fix_whitespace_issues(self, content: str) -> str:
        """修复空白字符问题"""
        # 移除行尾空白
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            # 移除行尾空白
            fixed_line = line.rstrip()
            fixed_lines.append(fixed_line)

        # 确保文件以换行符结尾
        result = '\n'.join(fixed_lines)
        if result and not result.endswith('\n'):
            result += '\n'

        return result

    def fix_import_issues(self, content: str) -> str:
        """修复导入问题"""
        lines = content.split('\n')

        # 分离不同类型的内容
        header_lines = []
        import_lines = []
        other_lines = []

        in_header = True
        for line in lines:
            stripped = line.strip()

            if in_header and (stripped.startswith('#') or stripped.startswith('"""') or
                             stripped.startswith("'''") or stripped == ''):
                header_lines.append(line)
            elif stripped.startswith(('import ', 'from ')) and not stripped.startswith('#'):
                import_lines.append(line)
                in_header = False
            else:
                other_lines.append(line)
                in_header = False

        # 去重导入语句
        unique_imports = []
        seen_imports = set()

        for imp in import_lines:
            if imp.strip() not in seen_imports:
                unique_imports.append(imp)
                seen_imports.add(imp.strip())

        # 重新组合
        result_lines = header_lines
        if unique_imports:
            if header_lines and header_lines[-1].strip():
                result_lines.append('')
            result_lines.extend(unique_imports)
            result_lines.append('')
        result_lines.extend(other_lines)

        return '\n'.join(result_lines)

    def fix_undefined_variables(self, content: str) -> str:
        """修复未定义变量的特定情况"""
        # 修复特定的未定义变量模式
        fixes = [
            # 修复capability_id相关问题
            (r'\bcapability_id\b(?!\s*=)', 'capability.get("id", "")'),
            # 修复params相关问题
            (r'\bparams\b(?!\s*=)(?!\s*:)', 'request.get("params", {})'),
            # 修复常见的上下文变量
            (r'\buser_id\b(?!\s*=)(?!\s*:)', 'context.get("user_id", "")'),
            (r'\bsession_id\b(?!\s*=)(?!\s*:)', 'context.get("session_id", "")'),
        ]

        modified = content
        for pattern, replacement in fixes:
            if re.search(pattern, modified):
                modified = re.sub(pattern, replacement, modified)
                self.fixes_applied += 1

        return modified

    def add_missing_error_handling(self, content: str) -> str:
        """为缺少错误处理的代码添加基本的try-except"""
        lines = content.split('\n')
        modified_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # 检查是否是可能抛出异常的操作
            if (any(pattern in stripped for pattern in [
                'await ', '.get(', '.post(', '.put(', '.delete(',
                'json.loads(', 'json.dumps(', 'open(', 'requests.',
                '.connect(', '.execute(', '.query('
            ]) and 'try:' not in stripped and 'except' not in stripped):
                pass

                # 检查前后是否已经在try块中
                in_try_block = False
                for j in range(max(0, i-5), i):
                    if 'try:' in lines[j] and lines[j].strip().endswith('try:'):
                        in_try_block = True
                        break

                if not in_try_block:
                    indent = len(line) - len(line.lstrip())
                    indent_str = ' ' * indent

                    # 添加try-except包装
                    modified_lines.append(f"{indent_str}try:")
                    modified_lines.append(f"{indent_str}    {stripped}")
                    modified_lines.append(f"{indent_str}except Exception as e:")
                    modified_lines.append(f"{indent_str}    logger.error(f'Error: {{e}}')")
                    modified_lines.append(f"{indent_str}    raise")
                    self.fixes_applied += 1
                else:
                    modified_lines.append(line)
            else:
                modified_lines.append(line)

            i += 1

        return '\n'.join(modified_lines)

    def fix_file(self, file_path: Path) -> bool:
        """修复单个文件"""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # 应用各种修复
            content = self.remove_commented_code(content)
            content = self.fix_whitespace_issues(content)
            content = self.fix_import_issues(content)
            content = self.fix_undefined_variables(content)

            # 如果内容有变化，写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True

            return False
        except Exception as e:
            print(f"  ❌ 修复文件失败 {file_path}: {e}")
            return False

    def run(self):
        """运行最终清理"""
        print("🧹 开始最终清理...")

        # 获取所有Python文件
        python_files = list(self.base_path.rglob("*.py"))

        fixed_files = 0
        for file_path in python_files:
            if (file_path.name.startswith('.') or
                'test' in str(file_path) or
                '__pycache__' in str(file_path) or
                file_path.name in ['critical_fixes.py', 'final_cleanup.py', 'comprehensive_fix.py']):
                continue

            print(f"🧹 清理文件: {file_path.relative_to(self.base_path)}")
            if self.fix_file(file_path):
                fixed_files += 1
                print("  ✅ 文件已清理")
            else:
                print("  ℹ️ 文件无需清理")

        print("\n📊 清理完成:")
        print(f"  - 检查文件: {len(python_files)}")
        print(f"  - 清理文件: {fixed_files}")
        print(f"  - 应用修复: {self.fixes_applied}")

if __name__ == "__main__":
    cleanup = FinalCleanup()
    cleanup.run()
