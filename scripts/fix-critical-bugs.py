#!/usr/bin/env python3
"""
索克生活项目关键Bug自动修复脚本
修复Python语法错误和常见问题
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class BugFixer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.error_files = []
        
    def fix_python_syntax_errors(self) -> Dict[str, int]:
        """修复Python语法错误"""
        stats = {
            'files_processed': 0,
            'files_fixed': 0,
            'errors_fixed': 0
        }
        
        # 查找所有Python文件
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
                
            stats['files_processed'] += 1
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # 修复常见语法错误
                content = self._fix_function_annotations(content)
                content = self._fix_import_statements(content)
                content = self._fix_indentation_errors(content)
                content = self._fix_colon_errors(content)
                
                # 检查是否有修改
                if content != original_content:
                    # 验证修复后的语法
                    try:
                        ast.parse(content)
                        # 语法正确，写入文件
                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        stats['files_fixed'] += 1
                        stats['errors_fixed'] += self._count_fixes(original_content, content)
                        self.fixed_files.append(str(py_file))
                        print(f"✅ 修复: {py_file}")
                        
                    except SyntaxError as e:
                        print(f"⚠️  修复后仍有语法错误: {py_file} - {e}")
                        self.error_files.append(str(py_file))
                        
            except Exception as e:
                print(f"❌ 处理文件失败: {py_file} - {e}")
                self.error_files.append(str(py_file))
        
        return stats
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = [
            'venv/', '__pycache__/', '.git/', 'node_modules/',
            'migrations/', 'htmlcov/', '.pytest_cache/',
            '_pb2.py', '_pb2_grpc.py',  # 跳过protobuf生成的文件
            'backup/', 'archive/',  # 跳过备份文件
            '.cache/', 'wheels-v5/'  # 跳过缓存文件
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def _fix_function_annotations(self, content: str) -> str:
        """修复函数类型注解错误"""
        # 修复 "def func() - > Type:" 为 "def func() -> Type:"
        content = re.sub(r'def\s+(\w+)\s*\([^)]*\)\s*-\s*>\s*([^:]+):', 
                        r'def \1() -> \2:', content)
        
        # 修复 "def func() - > None:" 为 "def func() -> None:"
        content = re.sub(r'def\s+(\w+)\s*\([^)]*\)\s*-\s*>\s*None\s*:', 
                        r'def \1() -> None:', content)
        
        return content
    
    def _fix_import_statements(self, content: str) -> str:
        """修复导入语句错误"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 修复 "from module import module" 错误
            if re.match(r'from\s+(\w+)\s+import\s+\1', line):
                module_name = re.match(r'from\s+(\w+)\s+import\s+\1', line).group(1)
                fixed_lines.append(f'import {module_name}')
            
            # 修复 "import self.module" 错误
            elif 'import self.' in line:
                continue  # 删除这种错误的导入
            
            # 修复重复导入
            elif line.startswith('import ') or line.startswith('from '):
                if line not in [l for l in fixed_lines if l.startswith(('import ', 'from '))]:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_indentation_errors(self, content: str) -> str:
        """修复缩进错误"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # 如果是只有pass的行且缩进不正确
            if line.strip() == 'pass':
                # 查找前一个非空行的缩进
                prev_indent = 0
                for j in range(i-1, -1, -1):
                    if lines[j].strip():
                        if lines[j].rstrip().endswith(':'):
                            prev_indent = len(lines[j]) - len(lines[j].lstrip()) + 4
                        else:
                            prev_indent = len(lines[j]) - len(lines[j].lstrip())
                        break
                
                fixed_lines.append(' ' * prev_indent + 'pass')
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_colon_errors(self, content: str) -> str:
        """修复冒号错误"""
        # 修复函数定义缺少冒号
        content = re.sub(r'(def\s+\w+\s*\([^)]*\)\s*(?:->.*?)?)$', 
                        r'\1:', content, flags=re.MULTILINE)
        
        # 修复类定义缺少冒号
        content = re.sub(r'(class\s+\w+(?:\([^)]*\))?)$', 
                        r'\1:', content, flags=re.MULTILINE)
        
        return content
    
    def _count_fixes(self, original: str, fixed: str) -> int:
        """统计修复的错误数量"""
        # 简单统计：比较行数差异
        return abs(len(original.split('\n')) - len(fixed.split('\n')))
    
    def generate_report(self, stats: Dict[str, int]) -> str:
        """生成修复报告"""
        report = f"""
# Bug修复报告

## 统计信息
- 处理文件数: {stats['files_processed']}
- 修复文件数: {stats['files_fixed']}
- 修复错误数: {stats['errors_fixed']}

## 修复成功的文件
"""
        for file in self.fixed_files:
            report += f"- {file}\n"
        
        if self.error_files:
            report += "\n## 仍有错误的文件\n"
            for file in self.error_files:
                report += f"- {file}\n"
        
        return report

def main():
    """主函数"""
    project_root = os.getcwd()
    
    print("🔧 开始修复索克生活项目的关键Bug...")
    
    fixer = BugFixer(project_root)
    stats = fixer.fix_python_syntax_errors()
    
    # 生成报告
    report = fixer.generate_report(stats)
    
    # 保存报告
    with open('bug_fix_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 修复完成!")
    print(f"📊 处理了 {stats['files_processed']} 个文件")
    print(f"🔧 修复了 {stats['files_fixed']} 个文件")
    print(f"🐛 修复了 {stats['errors_fixed']} 个错误")
    print(f"📄 详细报告已保存到 bug_fix_report.md")

if __name__ == "__main__":
    main() 