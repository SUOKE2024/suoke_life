#!/usr/bin/env python3
"""
索克生活微服务高级语法修复工具
处理复杂的语法错误，包括缩进、函数定义、try语句等
"""

import ast
import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedSyntaxFixer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues_fixed = 0
        self.files_processed = 0
        
    def analyze_syntax_error(self, file_path: Path, content: str) -> Tuple[str, int, str]:
        """分析语法错误类型和位置"""
        try:
            ast.parse(content)
            return "no_error", 0, ""
        except SyntaxError as e:
            return e.msg, e.lineno or 0, e.text or ""
            
    def fix_unexpected_indent(self, content: str, error_line: int) -> str:
        """修复unexpected indent错误"""
        lines = content.split('\n')
        
        if error_line > 0 and error_line <= len(lines):
            line_idx = error_line - 1
            line = lines[line_idx]
            
            # 如果行开头有缩进，移除它
            if line.startswith(('    ', '\t')):
                lines[line_idx] = line.lstrip()
                logger.info(f"移除第{error_line}行的意外缩进")
                
        return '\n'.join(lines)
        
    def fix_expected_indented_block(self, content: str, error_line: int) -> str:
        """修复expected indented block错误"""
        lines = content.split('\n')
        
        if error_line > 0 and error_line <= len(lines):
            line_idx = error_line - 1
            
            # 检查前一行是否以冒号结尾
            if line_idx > 0:
                prev_line = lines[line_idx - 1].strip()
                current_line = lines[line_idx].strip()
                
                if prev_line.endswith(':'):
                    if current_line == '':
                        # 空行，添加pass语句
                        lines[line_idx] = '    pass'
                        logger.info(f"在第{error_line}行添加pass语句")
                    elif not current_line.startswith(' '):
                        # 需要缩进
                        lines[line_idx] = '    ' + current_line
                        logger.info(f"为第{error_line}行添加缩进")
                        
        return '\n'.join(lines)
        
    def fix_function_definition_block(self, content: str, error_line: int) -> str:
        """修复函数定义后缺少缩进块的问题"""
        lines = content.split('\n')
        
        if error_line > 0 and error_line <= len(lines):
            line_idx = error_line - 1
            
            # 查找函数定义行
            for i in range(max(0, line_idx - 5), line_idx + 1):
                if i < len(lines) and lines[i].strip().startswith('def ') and lines[i].strip().endswith(':'):
                    # 找到函数定义，检查下一行
                    next_idx = i + 1
                    if next_idx < len(lines):
                        next_line = lines[next_idx].strip()
                        if next_line == '' or not next_line.startswith(' '):
                            # 添加pass语句
                            if next_line == '':
                                lines[next_idx] = '    pass'
                            else:
                                lines.insert(next_idx, '    pass')
                            logger.info(f"在函数定义后添加pass语句")
                            break
                            
        return '\n'.join(lines)
        
    def fix_try_statement_block(self, content: str, error_line: int) -> str:
        """修复try语句后缺少缩进块的问题"""
        lines = content.split('\n')
        
        if error_line > 0 and error_line <= len(lines):
            line_idx = error_line - 1
            
            # 查找try语句
            for i in range(max(0, line_idx - 3), line_idx + 1):
                if i < len(lines) and lines[i].strip() == 'try:':
                    # 找到try语句，检查下一行
                    next_idx = i + 1
                    if next_idx < len(lines):
                        next_line = lines[next_idx].strip()
                        if next_line == '' or not next_line.startswith(' '):
                            # 添加pass语句
                            if next_line == '':
                                lines[next_idx] = '    pass'
                            else:
                                lines.insert(next_idx, '    pass')
                            logger.info(f"在try语句后添加pass语句")
                            break
                            
        return '\n'.join(lines)
        
    def fix_invalid_syntax(self, content: str, error_line: int, error_text: str) -> str:
        """修复无效语法错误"""
        lines = content.split('\n')
        
        if error_line > 0 and error_line <= len(lines):
            line_idx = error_line - 1
            line = lines[line_idx]
            
            # 常见的无效语法修复
            
            # 修复多个import在同一行
            if 'import' in line and line.count('import') > 1:
                # 分割import语句
                if 'from' in line and 'import' in line:
                    parts = line.split('import')
                    if len(parts) > 2:
                        base = parts[0] + 'import ' + parts[1].strip()
                        lines[line_idx] = base
                        # 添加额外的import行
                        for j, part in enumerate(parts[2:], 1):
                            lines.insert(line_idx + j, f"from {parts[0].replace('from ', '').strip()} import {part.strip()}")
                        logger.info(f"分割第{error_line}行的多个import语句")
                        
            # 修复缺少冒号的语句
            elif any(keyword in line for keyword in ['if ', 'for ', 'while ', 'def ', 'class ', 'try', 'except', 'else', 'elif']):
                if not line.strip().endswith(':') and not line.strip().endswith('\\'):
                    lines[line_idx] = line.rstrip() + ':'
                    logger.info(f"为第{error_line}行添加冒号")
                    
            # 修复括号不匹配
            elif '(' in line and line.count('(') != line.count(')'):
                open_count = line.count('(')
                close_count = line.count(')')
                if open_count > close_count:
                    lines[line_idx] = line + ')' * (open_count - close_count)
                    logger.info(f"修复第{error_line}行的括号不匹配")
                    
        return '\n'.join(lines)
        
    def fix_file_comprehensive(self, file_path: Path) -> bool:
        """综合修复文件中的语法错误"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            max_iterations = 10  # 最大修复迭代次数
            iteration = 0
            
            while iteration < max_iterations:
                error_type, error_line, error_text = self.analyze_syntax_error(file_path, content)
                
                if error_type == "no_error":
                    break
                    
                logger.info(f"修复 {file_path}:{error_line} - {error_type}")
                
                # 根据错误类型选择修复方法
                if "unexpected indent" in error_type:
                    content = self.fix_unexpected_indent(content, error_line)
                elif "expected an indented block" in error_type:
                    if "function definition" in error_type:
                        content = self.fix_function_definition_block(content, error_line)
                    elif "try" in error_type:
                        content = self.fix_try_statement_block(content, error_line)
                    else:
                        content = self.fix_expected_indented_block(content, error_line)
                elif "invalid syntax" in error_type:
                    content = self.fix_invalid_syntax(content, error_line, error_text)
                else:
                    # 通用修复
                    content = self.fix_expected_indented_block(content, error_line)
                    
                iteration += 1
                
            # 验证最终结果
            try:
                ast.parse(content)
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"成功修复文件: {file_path}")
                    self.issues_fixed += 1
                    return True
                else:
                    logger.info(f"文件无需修复: {file_path}")
                    return True
            except SyntaxError as e:
                logger.error(f"文件修复后仍有语法错误 {file_path}:{e.lineno} - {e.msg}")
                return False
                
        except Exception as e:
            logger.error(f"修复文件失败 {file_path}: {e}")
            return False
            
    def fix_files_from_error_list(self, error_files: List[str]):
        """从错误文件列表中修复文件"""
        logger.info(f"开始修复 {len(error_files)} 个有语法错误的文件...")
        
        for file_str in error_files:
            # 直接使用文件路径
            file_path = self.project_root / file_str
            
            if file_path.exists():
                logger.info(f"修复文件: {file_path}")
                self.fix_file_comprehensive(file_path)
                self.files_processed += 1
            else:
                logger.warning(f"文件不存在: {file_path}")
                
        logger.info(f"修复完成! 处理了 {self.files_processed} 个文件，成功修复 {self.issues_fixed} 个文件")

def main():
    # 从之前的扫描结果中获取错误文件列表
    error_files = [
        "services/api-gateway/test/test_security_comprehensive.py",
        "services/api-gateway/test/test_performance.py",
        "services/api-gateway/utils/exception_handler.py",
        "services/api-gateway/suoke_api_gateway/main.py",
        "services/api-gateway/examples/websocket_client.py",
        "services/api-gateway/scripts/monitor.py",
        "services/api-gateway/scripts/benchmark.py",
        "services/api-gateway/pkg/utils/auth.py",
        "services/api-gateway/pkg/utils/consul_patch.py",
        "services/api-gateway/pkg/utils/config.py"
    ]
    
    fixer = AdvancedSyntaxFixer(".")
    fixer.fix_files_from_error_list(error_files)

if __name__ == "__main__":
    main()
