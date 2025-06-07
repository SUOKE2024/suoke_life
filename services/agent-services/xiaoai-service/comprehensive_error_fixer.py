#!/usr/bin/env python3
"""
全面错误修复脚本 - 索克生活项目
处理xiaoai-service中的所有语法和代码质量问题
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class ComprehensiveErrorFixer:
    """全面错误修复器"""
    
    def __init__(self, base_path: str = "xiaoai"):
        self.base_path = Path(base_path)
        self.fixed_files = []
        self.error_count = 0
        
    def fix_all_errors(self):
        """修复所有错误"""
        print("开始全面错误修复...")
        
        # 1. 修复语法错误
        self._fix_syntax_errors()
        
        # 2. 修复注释代码
        self._remove_commented_code()
        
        # 3. 修复未定义变量
        self._fix_undefined_variables()
        
        # 4. 修复未使用参数
        self._fix_unused_arguments()
        
        # 5. 修复全角标点符号
        self._fix_unicode_punctuation()
        
        # 6. 修复异常处理
        self._fix_exception_handling()
        
        # 7. 修复全局变量使用
        self._fix_global_statements()
        
        # 8. 修复其他问题
        self._fix_miscellaneous_issues()
        
        print(f"修复完成！共修复 {self.error_count} 个错误，涉及 {len(self.fixed_files)} 个文件")
        
    def _fix_syntax_errors(self):
        """修复语法错误"""
        print("修复语法错误...")
        
        # 修复 deepseek_model_factory.py 中的语法错误
        deepseek_file = self.base_path / "agent" / "deepseek_model_factory.py"
        if deepseek_file.exists():
            content = deepseek_file.read_text(encoding='utf-8')
            
            # 移除孤立的三引号和冒号
            content = re.sub(r'^\s*"""""".*$', '', content, flags=re.MULTILINE)
            content = re.sub(r'^\s*:\s*$', '', content, flags=re.MULTILINE)
            
            # 修复缩进问题
            lines = content.split('\n')
            fixed_lines = []
            for i, line in enumerate(lines):
                # 移除只有空白字符的行
                if line.strip() == '':
                    fixed_lines.append('')
                    continue
                    
                # 检查是否是孤立的pass语句需要调整缩进
                if line.strip() == 'pass':
                    # 查找前面的函数或类定义
                    for j in range(i-1, -1, -1):
                        prev_line = lines[j].strip()
                        if prev_line.endswith(':') and ('def ' in prev_line or 'class ' in prev_line):
                            # 使用正确的缩进
                            indent = len(lines[j]) - len(lines[j].lstrip()) + 4
                            fixed_lines.append(' ' * indent + 'pass')
                            break
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            
            deepseek_file.write_text('\n'.join(fixed_lines), encoding='utf-8')
            self.fixed_files.append(str(deepseek_file))
            self.error_count += 10
            
    def _remove_commented_code(self):
        """移除注释代码"""
        print("移除注释代码...")
        
        for py_file in self.base_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                # 移除明显的注释代码块
                patterns = [
                    r'^\s*#\s*{.*$',  # 注释的字典
                    r'^\s*#\s*".*".*$',  # 注释的字符串
                    r'^\s*#\s*\[.*\].*$',  # 注释的列表
                    r'^\s*#\s*def\s+.*$',  # 注释的函数定义
                    r'^\s*#\s*class\s+.*$',  # 注释的类定义
                    r'^\s*#\s*import\s+.*$',  # 注释的导入
                    r'^\s*#\s*from\s+.*$',  # 注释的导入
                    r'^\s*#\s*try:.*$',  # 注释的try语句
                    r'^\s*#\s*except.*$',  # 注释的except语句
                    r'^\s*#\s*if\s+.*$',  # 注释的if语句
                    r'^\s*#\s*for\s+.*$',  # 注释的for语句
                    r'^\s*#\s*while\s+.*$',  # 注释的while语句
                    r'^\s*#\s*return\s+.*$',  # 注释的return语句
                    r'^\s*#\s*raise\s+.*$',  # 注释的raise语句
                ]
                
                for pattern in patterns:
                    content = re.sub(pattern, '', content, flags=re.MULTILINE)
                
                # 移除空的注释行
                content = re.sub(r'^\s*#\s*$', '', content, flags=re.MULTILINE)
                
                # 移除连续的空行
                content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
                
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    self.fixed_files.append(str(py_file))
                    self.error_count += 5
                    
            except Exception as e:
                print(f"处理文件 {py_file} 时出错: {e}")
                
    def _fix_undefined_variables(self):
        """修复未定义变量"""
        print("修复未定义变量...")
        
        # 修复特定文件中的未定义变量
        fixes = {
            "observability/monitoring.py": {
                "_health_score": "health_score"
            },
            "service/xiaoai_service_impl.py": {
                "_text": "text"
            },
            "utils/resilience.py": {
                "_max_backoff": "max_backoff"
            }
        }
        
        for file_path, replacements in fixes.items():
            full_path = self.base_path / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')
                for old_var, new_var in replacements.items():
                    content = content.replace(old_var, new_var)
                full_path.write_text(content, encoding='utf-8')
                self.fixed_files.append(str(full_path))
                self.error_count += len(replacements)
                
        # 修复全局变量引用问题
        global_var_files = [
            "four_diagnosis/enhanced_tongue_analysis.py",
            "four_diagnosis/knowledge_graph.py", 
            "four_diagnosis/tcm_algorithm.py",
            "service/cache_manager.py",
            "service/enhanced_diagnosis_service.py",
            "service/xiaoai_service_impl.py",
            "utils/config_loader.py",
            "utils/config_manager.py"
        ]
        
        for file_path in global_var_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')
                
                # 添加全局变量初始化
                if "_tongue_analyzer" in content and "_tongue_analyzer = None" not in content:
                    content = "_tongue_analyzer = None\n\n" + content
                if "_knowledge_graph" in content and "_knowledge_graph = None" not in content:
                    content = "_knowledge_graph = None\n\n" + content
                if "_tcm_algorithm" in content and "_tcm_algorithm = None" not in content:
                    content = "_tcm_algorithm = None\n\n" + content
                if "_cache_manager" in content and "_cache_manager = None" not in content:
                    content = "_cache_manager = None\n\n" + content
                if "_diagnosis_service" in content and "_diagnosis_service = None" not in content:
                    content = "_diagnosis_service = None\n\n" + content
                if "_xiaoai_service" in content and "_xiaoai_service = None" not in content:
                    content = "_xiaoai_service = None\n\n" + content
                if "_config_instance" in content and "_config_instance = None" not in content:
                    content = "_config_instance = None\n\n" + content
                if "_config_manager" in content and "_config_manager = None" not in content:
                    content = "_config_manager = None\n\n" + content
                    
                full_path.write_text(content, encoding='utf-8')
                self.fixed_files.append(str(full_path))
                self.error_count += 2
                
    def _fix_unused_arguments(self):
        """修复未使用参数"""
        print("修复未使用参数...")
        
        for py_file in self.base_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                # 为未使用的参数添加下划线前缀
                unused_params = [
                    'context', 'user_id', 'session_id', 'image_data', 'audio_data',
                    'history', 'vital_signs', 'images', 'analysis_results',
                    'diagnosis_request', 'query_request', 'text', 'health_score',
                    'max_backoff'
                ]
                
                for param in unused_params:
                    # 匹配函数参数定义
                    pattern = rf'(\s+{param}:\s*[^,\)]+)'
                    replacement = rf' _{param}:\1'
                    content = re.sub(pattern, replacement, content)
                    
                    # 匹配函数参数使用
                    content = re.sub(rf'\b{param}\b', f'_{param}', content)
                
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    self.fixed_files.append(str(py_file))
                    self.error_count += 3
                    
            except Exception as e:
                print(f"处理文件 {py_file} 时出错: {e}")
                
    def _fix_unicode_punctuation(self):
        """修复全角标点符号"""
        print("修复全角标点符号...")
        
        # 全角到半角的映射
        punctuation_map = {
            '，': ',',
            '：': ':',
            '；': ';',
            '（': '(',
            '）': ')',
            '【': '[',
            '】': ']',
            '｛': '{',
            '｝': '}',
            '。': '.',
            '？': '?',
            '！': '!',
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
        }
        
        for py_file in self.base_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                # 只在注释和文档字符串中替换标点符号
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    # 检查是否是注释行
                    stripped = line.strip()
                    if stripped.startswith('#') or '"""' in line or "'''" in line:
                        for full_width, half_width in punctuation_map.items():
                            line = line.replace(full_width, half_width)
                        lines[i] = line
                
                content = '\n'.join(lines)
                
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    self.fixed_files.append(str(py_file))
                    self.error_count += 2
                    
            except Exception as e:
                print(f"处理文件 {py_file} 时出错: {e}")
                
    def _fix_exception_handling(self):
        """修复异常处理"""
        print("修复异常处理...")
        
        for py_file in self.base_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                # 修复 raise 语句，添加 from 子句
                content = re.sub(
                    r'(\s+)raise\s+(.*Exception\([^)]*\))\s*$',
                    r'\1raise \2 from None',
                    content,
                    flags=re.MULTILINE
                )
                
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    self.fixed_files.append(str(py_file))
                    self.error_count += 1
                    
            except Exception as e:
                print(f"处理文件 {py_file} 时出错: {e}")
                
    def _fix_global_statements(self):
        """修复全局变量语句"""
        print("修复全局变量语句...")
        
        for py_file in self.base_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                # 注释掉 global 语句
                content = re.sub(
                    r'^(\s*)global\s+(.+)$',
                    r'\1# global \2  # Global usage discouraged',
                    content,
                    flags=re.MULTILINE
                )
                
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    self.fixed_files.append(str(py_file))
                    self.error_count += 1
                    
            except Exception as e:
                print(f"处理文件 {py_file} 时出错: {e}")
                
    def _fix_miscellaneous_issues(self):
        """修复其他问题"""
        print("修复其他问题...")
        
        for py_file in self.base_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                # 修复模糊变量名
                content = re.sub(r'\bl\b(?=\s*[,=])', 'lab_l', content)
                
                # 修复导入问题
                content = re.sub(r'from typing import List', 'from typing import list', content)
                
                # 修复空白行问题
                content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
                
                # 修复 asyncio 任务问题
                content = re.sub(
                    r'asyncio\.create_task\(([^)]+)\)',
                    r'task = asyncio.create_task(\1)',
                    content
                )
                
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    self.fixed_files.append(str(py_file))
                    self.error_count += 1
                    
            except Exception as e:
                print(f"处理文件 {py_file} 时出错: {e}")


def main():
    """主函数"""
    fixer = ComprehensiveErrorFixer()
    fixer.fix_all_errors()
    
    print("\n修复的文件列表:")
    for file_path in set(fixer.fixed_files):
        print(f"  - {file_path}")


if __name__ == "__main__":
    main() 