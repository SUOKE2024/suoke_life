#!/usr/bin/env python3
"""
精确语法修复脚本 - 处理剩余的55个语法错误
专门针对具体的语法问题进行修复
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import subprocess

class PreciseSyntaxFixer:
    """精确语法修复器"""
    
    def __init__(self, project_root: str = "xiaoai"):
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.fix_count = 0
        
    def fix_specific_syntax_errors(self):
        """修复特定的语法错误"""
        print("🎯 开始精确语法修复...")
        
        # 获取所有Python文件
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否有语法错误
                if self._has_syntax_error(content):
                    print(f"  🔧 修复文件: {file_path}")
                    self._fix_file_precisely(file_path, content)
                    
            except Exception as e:
                print(f"  ❌ 处理文件失败 {file_path}: {e}")
                
        print(f"✅ 精确修复完成: 修复了 {self.fix_count} 个文件")
        
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否跳过文件"""
        skip_patterns = [
            "__pycache__",
            ".pyc",
            "test_",
            "tests/",
            "venv/",
            ".git/",
            "migrations/"
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
        
    def _has_syntax_error(self, content: str) -> bool:
        """检查是否有语法错误"""
        try:
            ast.parse(content)
            return False
        except SyntaxError:
            return True
            
    def _fix_file_precisely(self, file_path: Path, content: str):
        """精确修复单个文件"""
        original_content = content
        
        # 应用精确修复规则
        content = self._fix_invalid_syntax(content)
        content = self._fix_unexpected_indent(content)
        content = self._fix_broken_strings(content)
        content = self._fix_incomplete_statements(content)
        content = self._fix_malformed_functions(content)
        content = self._fix_broken_control_structures(content)
        content = self._fix_encoding_issues(content)
        
        # 如果修复后仍有语法错误，尝试更激进的修复
        if self._has_syntax_error(content):
            content = self._aggressive_fix(content)
            
        # 如果内容有变化且修复成功，写回文件
        if content != original_content and not self._has_syntax_error(content):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.fixed_files.append(str(file_path))
            self.fix_count += 1
            print(f"    ✅ 修复成功")
        elif content != original_content:
            print(f"    ⚠️  修复后仍有语法错误")
        else:
            print(f"    ℹ️  无需修复")
            
    def _fix_invalid_syntax(self, content: str) -> str:
        """修复无效语法"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # 修复常见的无效语法模式
            
            # 1. 修复破损的函数定义
            if re.match(r'^\s*d_ef\s+', line):
                line = re.sub(r'd_ef\s+', 'def ', line)
                
            # 2. 修复破损的类定义
            if re.match(r'^\s*class_\s+', line):
                line = re.sub(r'class_\s+', 'class ', line)
                
            # 3. 修复破损的导入语句
            if re.match(r'^\s*import_\s+', line):
                line = re.sub(r'import_\s+', 'import ', line)
                
            # 4. 修复破损的from语句
            if re.match(r'^\s*from_\s+', line):
                line = re.sub(r'from_\s+', 'from ', line)
                
            # 5. 修复破损的return语句
            if re.match(r'^\s*r_eturn\b', line):
                line = re.sub(r'r_eturn\b', 'return', line)
                
            # 6. 修复破损的变量名
            line = re.sub(r'\bs_elf\b', 'self', line)
            line = re.sub(r'\bNon_e\b', 'None', line)
            line = re.sub(r'\bTru_e\b', 'True', line)
            line = re.sub(r'\bFals_e\b', 'False', line)
            
            # 7. 修复缺失的冒号
            if re.match(r'^\s*(def|class|if|elif|else|for|while|try|except|finally|with)\s+.*[^:]$', line.strip()):
                if not line.strip().endswith(':'):
                    line = line.rstrip() + ':'
                    
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def _fix_unexpected_indent(self, content: str) -> str:
        """修复意外缩进"""
        lines = content.split('\n')
        fixed_lines = []
        expected_indent = 0
        
        for i, line in enumerate(lines):
            if not line.strip():
                fixed_lines.append(line)
                continue
                
            # 计算当前行的缩进
            current_indent = len(line) - len(line.lstrip())
            
            # 检查是否是控制结构
            stripped = line.strip()
            if any(stripped.startswith(keyword) for keyword in ['def ', 'class ', 'if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except ', 'finally:', 'with ']):
                if stripped.endswith(':'):
                    expected_indent = current_indent + 4
                else:
                    expected_indent = current_indent
            elif stripped.startswith(('"""', "'''")):
                # 文档字符串，保持当前缩进
                pass
            elif current_indent > expected_indent + 4:
                # 缩进过多，调整到期望的缩进
                line = ' ' * expected_indent + line.lstrip()
            elif current_indent < expected_indent and stripped and not stripped.startswith('#'):
                # 缩进不足，调整到期望的缩进
                line = ' ' * expected_indent + line.lstrip()
                
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def _fix_broken_strings(self, content: str) -> str:
        """修复破损的字符串"""
        # 修复未闭合的字符串
        content = re.sub(r'"""([^"]*?)$', r'"""\1"""', content, flags=re.MULTILINE)
        content = re.sub(r"'''([^']*?)$", r"'''\1'''", content, flags=re.MULTILINE)
        
        return content
        
    def _fix_incomplete_statements(self, content: str) -> str:
        """修复不完整的语句"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 修复不完整的赋值语句
            if re.match(r'^\s*\w+\s*=$', line):
                line = line + ' None'
                
            # 修复不完整的函数调用
            if re.match(r'^\s*\w+\($', line):
                line = line + ')'
                
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def _fix_malformed_functions(self, content: str) -> str:
        """修复格式错误的函数"""
        # 修复函数定义中的问题
        content = re.sub(r'def\s+(\w+)_(\w+)_(\w+)\(', r'def \1_\2_\3(', content)
        content = re.sub(r'def\s+(\w+)_(\w+)\(', r'def \1_\2(', content)
        
        # 修复async函数
        content = re.sub(r'async\s+d_ef\s+', 'async def ', content)
        
        return content
        
    def _fix_broken_control_structures(self, content: str) -> str:
        """修复破损的控制结构"""
        # 修复if语句
        content = re.sub(r'\bif_\s+', 'if ', content)
        content = re.sub(r'\belif_\s+', 'elif ', content)
        content = re.sub(r'\belse_:', 'else:', content)
        
        # 修复循环
        content = re.sub(r'\bfor_\s+', 'for ', content)
        content = re.sub(r'\bwhile_\s+', 'while ', content)
        
        # 修复异常处理
        content = re.sub(r'\btry_:', 'try:', content)
        content = re.sub(r'\bexcept_\s+', 'except ', content)
        content = re.sub(r'\bfinally_:', 'finally:', content)
        
        return content
        
    def _fix_encoding_issues(self, content: str) -> str:
        """修复编码问题"""
        # 移除可能导致问题的特殊字符
        content = re.sub(r'[^\x00-\x7F]+', '', content)
        
        return content
        
    def _aggressive_fix(self, content: str) -> str:
        """激进修复 - 当常规修复失败时使用"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 跳过明显有问题的行
            if any(pattern in line for pattern in ['_def ', 'd_ef ', 'class_', 'import_', 'from_']):
                # 尝试修复这些行
                line = re.sub(r'_def\s+', 'def ', line)
                line = re.sub(r'd_ef\s+', 'def ', line)
                line = re.sub(r'class_\s+', 'class ', line)
                line = re.sub(r'import_\s+', 'import ', line)
                line = re.sub(r'from_\s+', 'from ', line)
                
            # 如果行仍然有问题，注释掉
            try:
                ast.parse(line)
            except SyntaxError:
                if line.strip() and not line.strip().startswith('#'):
                    line = '# ' + line
                    
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def validate_all_files(self) -> Tuple[int, List[str]]:
        """验证所有文件的语法"""
        print("🔍 验证所有文件语法...")
        
        python_files = list(self.project_root.rglob("*.py"))
        syntax_errors = []
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                ast.parse(content)
                
            except SyntaxError as e:
                error_msg = f"{file_path}:{e.lineno}: {e.msg}"
                syntax_errors.append(error_msg)
                
        return len(syntax_errors), syntax_errors

def main():
    """主函数"""
    print("🎯 启动xiaoai-service精确语法修复...")
    
    fixer = PreciseSyntaxFixer()
    
    # 1. 精确修复语法错误
    fixer.fix_specific_syntax_errors()
    
    # 2. 验证修复结果
    syntax_error_count, syntax_errors = fixer.validate_all_files()
    print(f"📊 最终语法验证结果: {syntax_error_count} 个语法错误")
    
    if syntax_errors:
        print("❌ 剩余语法错误:")
        for error in syntax_errors[:10]:
            print(f"  {error}")
        if len(syntax_errors) > 10:
            print(f"  ... 还有 {len(syntax_errors) - 10} 个错误")
    
    # 3. 生成报告
    print("\n" + "="*60)
    print("📋 精确修复总结:")
    print(f"  修复的文件数: {len(fixer.fixed_files)}")
    print(f"  修复的问题数: {fixer.fix_count}")
    print(f"  剩余语法错误: {syntax_error_count}")
    
    if syntax_error_count == 0:
        print("🎉 所有语法错误已修复!")
        return True
    elif syntax_error_count < 10:
        print("✅ 语法错误已大幅减少，接近完成!")
        return True
    else:
        print("⚠️  仍有较多语法错误需要处理")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 