#!/usr/bin/env python3
"""
最终语法检查和修复脚本
找到并修复xiaoai-service中剩余的语法问题
"""

import ast
import os
from pathlib import Path
from typing import List, Tuple

class FinalSyntaxChecker:
    """最终语法检查器"""
    
    def __init__(self):
        self.syntax_errors = []
        
    def check_xiaoai_service(self):
        """检查xiaoai-service的语法问题"""
        print("🔍 检查xiaoai-service语法问题...")
        
        xiaoai_path = Path("xiaoai-service")
        if not xiaoai_path.exists():
            print("❌ xiaoai-service目录不存在")
            return
            
        python_files = list(xiaoai_path.rglob("*.py"))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查语法
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    self.syntax_errors.append({
                        'file': str(file_path),
                        'line': e.lineno,
                        'error': str(e),
                        'text': e.text
                    })
                    print(f"  ❌ 语法错误: {file_path}:{e.lineno} - {e.msg}")
                    
            except Exception as e:
                print(f"  ⚠️ 无法读取文件 {file_path}: {e}")
                
        if not self.syntax_errors:
            print("  ✅ 未发现语法错误")
        else:
            print(f"  🔧 发现 {len(self.syntax_errors)} 个语法错误")
            
        return self.syntax_errors
        
    def fix_syntax_errors(self):
        """修复语法错误"""
        if not self.syntax_errors:
            return
            
        print("🔧 开始修复语法错误...")
        
        for error in self.syntax_errors:
            file_path = Path(error['file'])
            print(f"  修复: {file_path}:{error['line']}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                # 尝试修复常见的语法错误
                if error['line'] <= len(lines):
                    line_content = lines[error['line'] - 1]
                    fixed_line = self._fix_line(line_content, error)
                    
                    if fixed_line != line_content:
                        lines[error['line'] - 1] = fixed_line
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                            
                        print(f"    ✅ 已修复: {error['line']}")
                    else:
                        print(f"    ⚠️ 无法自动修复: {error['error']}")
                        
            except Exception as e:
                print(f"    ❌ 修复失败: {e}")
                
    def _fix_line(self, line: str, error: dict) -> str:
        """修复单行语法错误"""
        original_line = line
        
        # 修复常见的语法错误
        
        # 1. 修复缺少冒号
        if "invalid syntax" in error['error'] and line.strip().endswith(')'):
            if any(keyword in line for keyword in ['if ', 'elif ', 'else', 'for ', 'while ', 'def ', 'class ', 'try', 'except', 'finally', 'with ']):
                if not line.rstrip().endswith(':'):
                    line = line.rstrip() + ':\n'
                    
        # 2. 修复缺少括号
        elif "unexpected EOF" in error['error']:
            open_parens = line.count('(') - line.count(')')
            open_brackets = line.count('[') - line.count(']')
            open_braces = line.count('{') - line.count('}')
            
            if open_parens > 0:
                line = line.rstrip() + ')' * open_parens + '\n'
            elif open_brackets > 0:
                line = line.rstrip() + ']' * open_brackets + '\n'
            elif open_braces > 0:
                line = line.rstrip() + '}' * open_braces + '\n'
                
        # 3. 修复缺少引号
        elif "unterminated string literal" in error['error']:
            if line.count('"') % 2 == 1:
                line = line.rstrip() + '"\n'
            elif line.count("'") % 2 == 1:
                line = line.rstrip() + "'\n"
                
        # 4. 修复缩进错误
        elif "IndentationError" in error['error']:
            # 简单的缩进修复
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                line = '    ' + line
                
        # 5. 修复非法字符
        elif "invalid character" in error['error']:
            # 移除非ASCII字符
            line = ''.join(char for char in line if ord(char) < 128)
            
        return line
        
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否跳过文件"""
        skip_patterns = [
            "__pycache__",
            ".pyc",
            "venv/",
            ".git/",
            "node_modules/",
            "test_",
            "_test.py"
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)

def main():
    """主函数"""
    print("🚀 启动最终语法检查和修复...")
    
    checker = FinalSyntaxChecker()
    
    # 检查语法错误
    errors = checker.check_xiaoai_service()
    
    if errors:
        # 修复语法错误
        checker.fix_syntax_errors()
        
        # 再次检查
        print("\n🔍 再次检查语法...")
        checker.syntax_errors = []
        remaining_errors = checker.check_xiaoai_service()
        
        if not remaining_errors:
            print("🎉 所有语法错误已修复！")
        else:
            print(f"⚠️ 还有 {len(remaining_errors)} 个语法错误需要手动修复")
    else:
        print("🎉 xiaoai-service语法完美！")

if __name__ == "__main__":
    main() 