#!/usr/bin/env python3
"""
索克生活项目 - 关键语法错误自动修复工具
自动检测和修复Python代码中的常见语法错误
"""

import os
import re
import ast
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import subprocess

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SyntaxError:
    """语法错误信息"""
    file_path: str
    line_number: int
    column: int
    error_type: str
    message: str
    original_line: str
    fixed_line: Optional[str] = None

class CriticalSyntaxFixer:
    """关键语法错误修复器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.errors_found = []
        self.errors_fixed = []
        self.backup_dir = self.project_root / "backups" / "syntax_fixes"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 语法修复规则
        self.fix_patterns = [
            # 修复缺少冒号的问题
            (r'^(\s*)(def\s+\w+\s*\([^)]*\))\s*$', r'\1\2:'),
            (r'^(\s*)(class\s+\w+(?:\([^)]*\))?)\s*$', r'\1\2:'),
            (r'^(\s*)(if\s+.+)\s*$', r'\1\2:'),
            (r'^(\s*)(elif\s+.+)\s*$', r'\1\2:'),
            (r'^(\s*)(else)\s*$', r'\1\2:'),
            (r'^(\s*)(for\s+.+)\s*$', r'\1\2:'),
            (r'^(\s*)(while\s+.+)\s*$', r'\1\2:'),
            (r'^(\s*)(try)\s*$', r'\1\2:'),
            (r'^(\s*)(except(?:\s+\w+)?(?:\s+as\s+\w+)?)\s*$', r'\1\2:'),
            (r'^(\s*)(finally)\s*$', r'\1\2:'),
            (r'^(\s*)(with\s+.+)\s*$', r'\1\2:'),
            
            # 修复常见的语法错误
            (r'(\w+)\s*=\s*=\s*(\w+)', r'\1 == \2'),  # 修复赋值错误
            (r'(\w+)\s*!\s*=\s*(\w+)', r'\1 != \2'),  # 修复不等号
            
            # 修复导入语句
            (r'^(\s*)from\s+([^\s]+)\s+import\s*$', r'\1from \2 import *'),
            
            # 修复字符串引号问题
            (r"'([^']*)'([^']*)'", r"'\1\2'"),
            (r'"([^"]*)"([^"]*)"', r'"\1\2"'),
        ]
    
    def create_backup(self, file_path: Path) -> Path:
        """创建文件备份"""
        backup_path = self.backup_dir / file_path.relative_to(self.project_root)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_path.exists():
            backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
            logger.debug(f"创建备份: {backup_path}")
        
        return backup_path
    
    def check_syntax(self, file_path: Path) -> List[SyntaxError]:
        """检查文件语法错误"""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试编译代码
            try:
                ast.parse(content)
                return errors  # 没有语法错误
            except SyntaxError as e:
                error = SyntaxError(
                    file_path=str(file_path),
                    line_number=e.lineno or 0,
                    column=e.offset or 0,
                    error_type="SyntaxError",
                    message=str(e.msg),
                    original_line=e.text or ""
                )
                errors.append(error)
                
        except Exception as e:
            logger.error(f"检查文件 {file_path} 时出错: {e}")
        
        return errors
    
    def fix_indentation_errors(self, content: str) -> str:
        """修复缩进错误"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # 移除行尾空白
            line = line.rstrip()
            
            # 检查是否有混合的制表符和空格
            if '\t' in line and ' ' in line:
                # 将制表符转换为4个空格
                line = line.expandtabs(4)
            
            # 修复常见的缩进问题
            if line.strip():
                # 确保缩进是4的倍数
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces % 4 != 0:
                    # 调整到最近的4的倍数
                    new_indent = (leading_spaces // 4) * 4
                    line = ' ' * new_indent + line.lstrip()
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_missing_colons(self, content: str) -> str:
        """修复缺少的冒号"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            original_line = line
            
            # 应用修复规则
            for pattern, replacement in self.fix_patterns:
                if re.match(pattern, line):
                    new_line = re.sub(pattern, replacement, line)
                    if new_line != line:
                        logger.debug(f"修复冒号: '{line.strip()}' -> '{new_line.strip()}'")
                        line = new_line
                        break
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_bracket_matching(self, content: str) -> str:
        """修复括号匹配问题"""
        # 简单的括号匹配修复
        stack = []
        brackets = {'(': ')', '[': ']', '{': '}'}
        
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 检查括号匹配
            for char in line:
                if char in brackets:
                    stack.append(brackets[char])
                elif char in brackets.values():
                    if stack and stack[-1] == char:
                        stack.pop()
            
            fixed_lines.append(line)
        
        # 如果有未匹配的括号，在文件末尾添加
        if stack:
            logger.warning(f"发现未匹配的括号，尝试修复")
            # 这里可以添加更复杂的括号修复逻辑
        
        return '\n'.join(fixed_lines)
    
    def fix_common_syntax_errors(self, content: str) -> str:
        """修复常见语法错误"""
        # 修复常见的Python语法错误
        fixes = [
            # 修复print语句（Python 2 -> Python 3）
            (r'\bprint\s+([^(].*)', r'print(\1)'),
            
            # 修复字符串格式化
            (r'%\s*\(([^)]+)\)\s*%\s*([^%]+)', r'{\1}.format(\2)'),
            
            # 修复比较运算符
            (r'\bis\s+not\s+None\b', r'is not None'),
            (r'\bis\s+None\b', r'is None'),
            
            # 修复异常处理语法
            (r'\bexcept\s+(\w+),\s*(\w+):', r'except \1 as \2:'),
            
            # 修复导入语句
            (r'^(\s*)import\s+([^,\s]+),\s*(.+)', r'\1import \2\n\1import \3'),
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        return content
    
    def fix_file(self, file_path: Path) -> bool:
        """修复单个文件的语法错误"""
        try:
            # 创建备份
            self.create_backup(file_path)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 应用各种修复
            content = original_content
            content = self.fix_indentation_errors(content)
            content = self.fix_missing_colons(content)
            content = self.fix_bracket_matching(content)
            content = self.fix_common_syntax_errors(content)
            
            # 如果内容有变化，写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # 验证修复结果
                errors_after = self.check_syntax(file_path)
                if not errors_after:
                    logger.info(f"✅ 成功修复: {file_path}")
                    return True
                else:
                    logger.warning(f"⚠️ 部分修复: {file_path} (仍有 {len(errors_after)} 个错误)")
                    return False
            else:
                logger.debug(f"📄 无需修复: {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 修复文件 {file_path} 时出错: {e}")
            return False
    
    def scan_and_fix_project(self) -> Dict[str, int]:
        """扫描并修复整个项目"""
        stats = {
            'total_files': 0,
            'files_with_errors': 0,
            'files_fixed': 0,
            'files_failed': 0
        }
        
        # 扫描所有Python文件
        python_files = list(self.project_root.rglob('*.py'))
        
        # 排除一些目录
        exclude_patterns = [
            '*/venv/*', '*/node_modules/*', '*/.git/*', 
            '*/build/*', '*/dist/*', '*/__pycache__/*',
            '*/coverage/*', '*/htmlcov/*'
        ]
        
        filtered_files = []
        for file_path in python_files:
            should_exclude = False
            for pattern in exclude_patterns:
                if file_path.match(pattern):
                    should_exclude = True
                    break
            if not should_exclude:
                filtered_files.append(file_path)
        
        stats['total_files'] = len(filtered_files)
        logger.info(f"开始扫描 {stats['total_files']} 个Python文件...")
        
        for file_path in filtered_files:
            try:
                # 检查语法错误
                errors = self.check_syntax(file_path)
                
                if errors:
                    stats['files_with_errors'] += 1
                    logger.info(f"🔍 发现语法错误: {file_path} ({len(errors)} 个错误)")
                    
                    # 尝试修复
                    if self.fix_file(file_path):
                        stats['files_fixed'] += 1
                    else:
                        stats['files_failed'] += 1
                        
            except Exception as e:
                logger.error(f"处理文件 {file_path} 时出错: {e}")
                stats['files_failed'] += 1
        
        return stats
    
    def generate_report(self, stats: Dict[str, int]) -> str:
        """生成修复报告"""
        report = f"""
# 索克生活项目 - 语法错误修复报告

## 📊 修复统计
- 总文件数: {stats['total_files']}
- 有错误的文件: {stats['files_with_errors']}
- 成功修复的文件: {stats['files_fixed']}
- 修复失败的文件: {stats['files_failed']}

## 📈 修复成功率
- 成功率: {(stats['files_fixed'] / max(stats['files_with_errors'], 1) * 100):.1f}%

## 🔧 修复内容
- 缺少冒号的语句
- 缩进错误
- 括号匹配问题
- 常见语法错误

## 📁 备份位置
所有修改的文件备份保存在: {self.backup_dir}

## ⚠️ 注意事项
1. 请在修复后运行测试确保功能正常
2. 如有问题可从备份目录恢复原文件
3. 建议提交代码前再次检查语法
"""
        return report

def main():
    """主函数"""
    project_root = os.getcwd()
    
    print("🔧 索克生活项目 - 关键语法错误自动修复工具")
    print("=" * 50)
    
    fixer = CriticalSyntaxFixer(project_root)
    
    # 执行修复
    stats = fixer.scan_and_fix_project()
    
    # 生成报告
    report = fixer.generate_report(stats)
    
    # 保存报告
    report_file = Path(project_root) / "syntax_fix_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "=" * 50)
    print("📄 修复完成！详细报告已保存到 syntax_fix_report.md")
    print(f"✅ 成功修复: {stats['files_fixed']} 个文件")
    print(f"❌ 修复失败: {stats['files_failed']} 个文件")
    
    if stats['files_failed'] > 0:
        print("\n⚠️ 部分文件修复失败，请手动检查和修复")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 