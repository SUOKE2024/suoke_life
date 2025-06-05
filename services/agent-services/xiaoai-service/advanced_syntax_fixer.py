#!/usr/bin/env python3
"""
高级语法修复脚本 - 专门处理xiaoai-service的语法错误
目标：修复497个语法错误和1709个未定义名称问题
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import subprocess

class AdvancedSyntaxFixer:
    """高级语法修复器"""
    
    def __init__(self, project_root: str = "xiaoai"):
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.error_count = 0
        self.fix_count = 0
        
    def fix_syntax_errors(self):
        """修复语法错误"""
        print("🔧 开始高级语法修复...")
        
        # 获取所有Python文件
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            print(f"  📝 修复文件: {file_path}")
            self._fix_file_syntax(file_path)
            
        print(f"✅ 语法修复完成: 修复了 {self.fix_count} 个问题")
        
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
        
    def _fix_file_syntax(self, file_path: Path):
        """修复单个文件的语法错误"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # 应用各种修复规则
            content = self._fix_broken_function_definitions(content)
            content = self._fix_broken_variable_names(content)
            content = self._fix_broken_imports(content)
            content = self._fix_broken_class_definitions(content)
            content = self._fix_broken_return_statements(content)
            content = self._fix_broken_assignments(content)
            content = self._fix_indentation_errors(content)
            content = self._fix_missing_colons(content)
            content = self._fix_broken_decorators(content)
            content = self._fix_type_annotations(content)
            
            # 如果内容有变化，写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixed_files.append(str(file_path))
                self.fix_count += 1
                
        except Exception as e:
            print(f"  ❌ 修复文件失败 {file_path}: {e}")
            
    def _fix_broken_function_definitions(self, content: str) -> str:
        """修复破损的函数定义"""
        # 修复 d_ef -> def
        content = re.sub(r'\bd_ef\b', 'def', content)
        
        # 修复 async d_ef -> async def
        content = re.sub(r'\basync\s+d_ef\b', 'async def', content)
        
        # 修复函数名中的下划线问题
        content = re.sub(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*?)_([a-zA-Z_][a-zA-Z0-9_]*?)\(', 
                        r'def \1_\2(', content)
        
        # 修复参数中的类型注解问题
        content = re.sub(r'(\w+)_(\w+):\s*(\w+)', r'\1_\2: \3', content)
        
        return content
        
    def _fix_broken_variable_names(self, content: str) -> str:
        """修复破损的变量名"""
        # 修复常见的变量名问题
        fixes = {
            r'\bs_elf\b': 'self',
            r'\bNon_e\b': 'None',
            r'\bTru_e\b': 'True',
            r'\bFals_e\b': 'False',
            r'\btyp_e\b': 'type',
            r'\bstr_\b': 'str',
            r'\bint_\b': 'int',
            r'\bfloat_\b': 'float',
            r'\blist_\b': 'list',
            r'\bdict_\b': 'dict',
            r'\br_eturn\b': 'return',
            r'\bif_\b': 'if',
            r'\bels_e\b': 'else',
            r'\belif_\b': 'elif',
            r'\bfor_\b': 'for',
            r'\bwhil_e\b': 'while',
            r'\btry_\b': 'try',
            r'\bexcept_\b': 'except',
            r'\bfinally_\b': 'finally',
            r'\bwith_\b': 'with',
            r'\bclass_\b': 'class',
            r'\bimport_\b': 'import',
            r'\bfrom_\b': 'from',
            r'\bas_\b': 'as',
            r'\bin_\b': 'in',
            r'\bis_\b': 'is',
            r'\bnot_\b': 'not',
            r'\band_\b': 'and',
            r'\bor_\b': 'or',
        }
        
        for pattern, replacement in fixes.items():
            content = re.sub(pattern, replacement, content)
            
        return content
        
    def _fix_broken_imports(self, content: str) -> str:
        """修复破损的导入语句"""
        # 修复导入语句中的下划线问题
        content = re.sub(r'from\s+(\w+)_(\w+)', r'from \1_\2', content)
        content = re.sub(r'import\s+(\w+)_(\w+)', r'import \1_\2', content)
        
        return content
        
    def _fix_broken_class_definitions(self, content: str) -> str:
        """修复破损的类定义"""
        # 修复类名中的问题
        content = re.sub(r'class\s+(\w+)_(\w+)', r'class \1_\2', content)
        
        return content
        
    def _fix_broken_return_statements(self, content: str) -> str:
        """修复破损的return语句"""
        # 修复 r_eturn -> return
        content = re.sub(r'\br_eturn\b', 'return', content)
        
        return content
        
    def _fix_broken_assignments(self, content: str) -> str:
        """修复破损的赋值语句"""
        # 修复变量赋值中的问题
        content = re.sub(r'(\w+)_(\w+)\s*=', r'\1_\2 =', content)
        
        return content
        
    def _fix_indentation_errors(self, content: str) -> str:
        """修复缩进错误"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # 检查是否是函数定义后的文档字符串
            if i > 0 and lines[i-1].strip().endswith(':'):
                if line.strip().startswith('"""') or line.strip().startswith("'''"):
                    # 确保文档字符串有正确的缩进
                    if not line.startswith('    '):
                        line = '    ' + line.lstrip()
                        
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def _fix_missing_colons(self, content: str) -> str:
        """修复缺失的冒号"""
        # 修复函数定义缺失的冒号
        content = re.sub(r'(def\s+\w+\([^)]*\))\s*$', r'\1:', content, flags=re.MULTILINE)
        
        # 修复类定义缺失的冒号
        content = re.sub(r'(class\s+\w+(?:\([^)]*\))?)\s*$', r'\1:', content, flags=re.MULTILINE)
        
        return content
        
    def _fix_broken_decorators(self, content: str) -> str:
        """修复破损的装饰器"""
        # 修复装饰器中的问题
        content = re.sub(r'@(\w+)_(\w+)', r'@\1_\2', content)
        
        return content
        
    def _fix_type_annotations(self, content: str) -> str:
        """修复类型注解问题"""
        # 修复类型注解中的问题
        content = re.sub(r':\s*(\w+)_(\w+)', r': \1_\2', content)
        content = re.sub(r':\s*(\w+)\s*\|\s*(\w+)_(\w+)', r': \1 | \2_\3', content)
        
        return content
        
    def validate_syntax(self) -> Tuple[int, List[str]]:
        """验证语法修复结果"""
        print("🔍 验证语法修复结果...")
        
        python_files = list(self.project_root.rglob("*.py"))
        syntax_errors = []
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 尝试解析AST
                ast.parse(content)
                
            except SyntaxError as e:
                error_msg = f"{file_path}:{e.lineno}: {e.msg}"
                syntax_errors.append(error_msg)
                
        return len(syntax_errors), syntax_errors
        
    def run_ruff_check(self) -> Tuple[int, str]:
        """运行ruff检查"""
        try:
            result = subprocess.run(
                ['ruff', 'check', str(self.project_root), '--output-format=text'],
                capture_output=True,
                text=True,
                cwd='.'
            )
            
            # 统计错误数量
            error_lines = [line for line in result.stdout.split('\n') if line.strip()]
            error_count = len([line for line in error_lines if ':' in line and ('error' in line.lower() or 'E' in line or 'F' in line)])
            
            return error_count, result.stdout
            
        except Exception as e:
            print(f"❌ Ruff检查失败: {e}")
            return -1, str(e)

def main():
    """主函数"""
    print("🚀 启动xiaoai-service高级语法修复...")
    
    fixer = AdvancedSyntaxFixer()
    
    # 1. 修复语法错误
    fixer.fix_syntax_errors()
    
    # 2. 验证语法
    syntax_error_count, syntax_errors = fixer.validate_syntax()
    print(f"📊 语法验证结果: {syntax_error_count} 个语法错误")
    
    if syntax_errors:
        print("❌ 剩余语法错误:")
        for error in syntax_errors[:10]:  # 只显示前10个
            print(f"  {error}")
        if len(syntax_errors) > 10:
            print(f"  ... 还有 {len(syntax_errors) - 10} 个错误")
    
    # 3. 运行ruff检查
    ruff_error_count, ruff_output = fixer.run_ruff_check()
    if ruff_error_count >= 0:
        print(f"📊 Ruff检查结果: {ruff_error_count} 个问题")
    
    # 4. 生成报告
    print("\n" + "="*60)
    print("📋 修复总结:")
    print(f"  修复的文件数: {len(fixer.fixed_files)}")
    print(f"  修复的问题数: {fixer.fix_count}")
    print(f"  剩余语法错误: {syntax_error_count}")
    print(f"  剩余代码问题: {ruff_error_count}")
    
    if syntax_error_count == 0:
        print("🎉 所有语法错误已修复!")
        return True
    else:
        print("⚠️  仍有语法错误需要手动修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 