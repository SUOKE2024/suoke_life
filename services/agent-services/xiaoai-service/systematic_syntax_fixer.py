#!/usr/bin/env python3
"""
系统性语法错误修复脚本 - 索克生活项目
专门修复Python语法问题，确保代码可以正常解析
"""

import ast
import re
from pathlib import Path
from typing import List, Tuple


class SystematicSyntaxFixer:
    """系统性语法错误修复器"""
    
    def __init__(self, base_path: str = "xiaoai"):
        self.base_path = Path(base_path)
        self.fixed_files = []
        self.error_count = 0
        
    def fix_all_syntax_errors(self):
        """修复所有语法错误"""
        print("开始系统性语法错误修复...")
        
        # 获取所有Python文件
        python_files = list(self.base_path.rglob("*.py"))
        print(f"找到 {len(python_files)} 个Python文件")
        
        for file_path in python_files:
            try:
                self._fix_file_syntax(file_path)
            except Exception as e:
                print(f"修复文件 {file_path} 时出错: {e}")
                
        print(f"语法错误修复完成！修复了 {len(self.fixed_files)} 个文件，共修复 {self.error_count} 个错误")
        
    def _fix_file_syntax(self, file_path: Path):
        """修复单个文件的语法错误"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # 1. 修复缺失的冒号
            content = self._fix_missing_colons(content)
            
            # 2. 修复缺失的引号
            content = self._fix_missing_quotes(content)
            
            # 3. 修复缺失的括号
            content = self._fix_missing_parentheses(content)
            
            # 4. 修复缩进问题
            content = self._fix_indentation_issues(content)
            
            # 5. 修复导入语句
            content = self._fix_import_statements(content)
            
            # 6. 移除注释代码
            content = self._remove_commented_code(content)
            
            # 7. 修复全角字符
            content = self._fix_unicode_characters(content)
            
            # 8. 验证语法
            if self._validate_syntax(content):
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.fixed_files.append(str(file_path))
                    self.error_count += 1
                    print(f"修复文件: {file_path}")
            else:
                print(f"语法验证失败: {file_path}")
                
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            
    def _fix_missing_colons(self, content: str) -> str:
        """修复缺失的冒号"""
        # 修复 if/elif/else 语句
        content = re.sub(r'\b(if|elif|else)\s+([^:\n]+)(?<![:\s])\s*\n', r'\1 \2:\n', content)
        
        # 修复 for/while 语句
        content = re.sub(r'\b(for|while)\s+([^:\n]+)(?<![:\s])\s*\n', r'\1 \2:\n', content)
        
        # 修复 try/except/finally 语句
        content = re.sub(r'\b(try|except|finally)\s*([^:\n]*)(?<![:\s])\s*\n', r'\1\2:\n', content)
        
        # 修复函数定义
        content = re.sub(r'\bdef\s+([^:\n]+)(?<![:\s])\s*\n', r'def \1:\n', content)
        
        # 修复类定义
        content = re.sub(r'\bclass\s+([^:\n]+)(?<![:\s])\s*\n', r'class \1:\n', content)
        
        return content
        
    def _fix_missing_quotes(self, content: str) -> str:
        """修复缺失的引号"""
        # 这个比较复杂，暂时跳过
        return content
        
    def _fix_missing_parentheses(self, content: str) -> str:
        """修复缺失的括号"""
        # 修复函数调用缺失的括号
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 简单的函数调用修复
            if re.search(r'\w+\s*\.\s*\w+\s*$', line.strip()) and not line.strip().endswith(')'):
                line = re.sub(r'(\w+\s*\.\s*\w+)\s*$', r'\1()', line)
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def _fix_indentation_issues(self, content: str) -> str:
        """修复缩进问题"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # 跳过空行
            if not line.strip():
                fixed_lines.append(line)
                continue
                
            # 修复混合缩进
            if '\t' in line and ' ' in line:
                # 将制表符转换为4个空格
                line = line.expandtabs(4)
                
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def _fix_import_statements(self, content: str) -> str:
        """修复导入语句"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 修复 from ... import 语句
            if line.strip().startswith('from ') and ' import ' in line:
                # 确保语法正确
                if not re.match(r'from\s+[\w.]+\s+import\s+[\w,\s*]+', line.strip()):
                    # 尝试修复
                    line = re.sub(r'from\s+([\w.]+)\s+import\s*(.*)', r'from \1 import \2', line)
                    
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def _remove_commented_code(self, content: str) -> str:
        """移除注释代码"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # 跳过文档字符串
            if stripped.startswith('"""') or stripped.startswith("'''"):
                fixed_lines.append(line)
                continue
                
            # 移除明显的注释代码
            if (stripped.startswith('# ') and 
                any(keyword in stripped for keyword in ['def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while '])):
                continue
                
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def _fix_unicode_characters(self, content: str) -> str:
        """修复全角字符"""
        # 修复全角标点符号
        replacements = {
            '，': ',',
            '。': '.',
            '：': ':',
            '；': ';',
            '（': '(',
            '）': ')',
            '【': '[',
            '】': ']',
            '｛': '{',
            '｝': '}',
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
            
        return content
        
    def _validate_syntax(self, content: str) -> bool:
        """验证Python语法"""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False
        except Exception:
            return False


if __name__ == "__main__":
    fixer = SystematicSyntaxFixer()
    fixer.fix_all_syntax_errors() 