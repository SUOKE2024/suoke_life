"""
comprehensive_syntax_fixer - 索克生活项目模块
"""

from pathlib import Path
from typing import List, Dict, Tuple, Optional
import ast
import logging
import os
import re
import sys

#!/usr/bin/env python3
"""
索克生活 - 全面语法修复工具
自动修复Python语法错误，确保代码质量
"""


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveSyntaxFixer:
    """全面的语法修复器"""
    
    def __init__(self, service_path: str):
        self.service_path = Path(service_path)
        self.fixed_files = []
        self.error_count = 0
        
    def fix_all_syntax_errors(self) -> bool:
        """修复所有语法错误"""
        logger.info(f"🚀 开始修复 {self.service_path.name} 的语法错误...")
        
        # 获取所有Python文件
        python_files = list(self.service_path.rglob("*.py"))
        
        for file_path in python_files:
            try:
                self.fix_file_syntax(file_path)
            except Exception as e:
                logger.error(f"修复文件 {file_path} 时出错: {e}")
                
        logger.info(f"✅ 修复完成！共修复 {len(self.fixed_files)} 个文件")
        return len(self.fixed_files) > 0
    
    def fix_file_syntax(self, file_path: Path) -> bool:
        """修复单个文件的语法错误"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否有语法错误
            try:
                ast.parse(content)
                return False  # 没有语法错误
            except SyntaxError as e:
                logger.info(f"🔧 修复文件: {file_path.relative_to(self.service_path)}")
                
                # 应用各种修复策略
                fixed_content = self.apply_fixes(content, file_path)
                
                # 验证修复结果
                try:
                    ast.parse(fixed_content)
                    # 写入修复后的内容
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    
                    self.fixed_files.append(str(file_path))
                    logger.info(f"  ✅ 成功修复: {file_path.name}")
                    return True
                    
                except SyntaxError as verify_error:
                    logger.warning(f"  ⚠️ 修复验证失败: {verify_error}")
                    return False
                    
        except Exception as e:
            logger.error(f"处理文件 {file_path} 时出错: {e}")
            return False
    
    def apply_fixes(self, content: str, file_path: Path) -> str:
        """应用各种修复策略"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            fixed_line = line
            
            # 修复策略1: 修复缺失的缩进块
            fixed_line = self.fix_missing_indent_blocks(fixed_line, i, lines)
            
            # 修复策略2: 修复意外的缩进
            fixed_line = self.fix_unexpected_indent(fixed_line, i, lines)
            
            # 修复策略3: 修复缩进不匹配
            fixed_line = self.fix_unmatched_indent(fixed_line, i, lines)
            
            # 修复策略4: 修复赋值表达式错误
            fixed_line = self.fix_assignment_expression(fixed_line)
            
            # 修复策略5: 修复无效语法
            fixed_line = self.fix_invalid_syntax(fixed_line, i, lines)
            
            fixed_lines.append(fixed_line)
        
        return '\n'.join(fixed_lines)
    
    def fix_missing_indent_blocks(self, line: str, line_num: int, lines: List[str]) -> str:
        """修复缺失的缩进块"""
        # 检查是否是需要缩进块的语句
        stripped = line.strip()
        
        if (stripped.endswith(':') and 
            any(keyword in stripped for keyword in ['def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except', 'with ', 'else:', 'elif '])):
            
            # 检查下一行是否有内容
            if line_num + 1 < len(lines):
                next_line = lines[line_num + 1].strip()
                if not next_line or not next_line.startswith(' '):
                    # 需要添加缩进块
                    current_indent = len(line) - len(line.lstrip())
                    return line
            
        return line
    
    def fix_unexpected_indent(self, line: str, line_num: int, lines: List[str]) -> str:
        """修复意外的缩进"""
        if line.strip() and line.startswith(' '):
            # 检查前一行的缩进级别
            if line_num > 0:
                prev_line = lines[line_num - 1]
                if prev_line.strip():
                    prev_indent = len(prev_line) - len(prev_line.lstrip())
                    current_indent = len(line) - len(line.lstrip())
                    
                    # 如果当前行缩进过多，调整缩进
                    if current_indent > prev_indent + 4:
                        # 调整为合理的缩进级别
                        expected_indent = prev_indent + 4 if prev_line.strip().endswith(':') else prev_indent
                        return ' ' * expected_indent + line.lstrip()
        
        return line
    
    def fix_unmatched_indent(self, line: str, line_num: int, lines: List[str]) -> str:
        """修复缩进不匹配"""
        if not line.strip():
            return line
            
        current_indent = len(line) - len(line.lstrip())
        
        # 查找合适的缩进级别
        for i in range(line_num - 1, -1, -1):
            if lines[i].strip():
                prev_indent = len(lines[i]) - len(lines[i].lstrip())
                
                # 如果是函数或类定义后的第一行
                if lines[i].strip().endswith(':'):
                    expected_indent = prev_indent + 4
                    if current_indent != expected_indent:
                        return ' ' * expected_indent + line.lstrip()
                break
        
        return line
    
    def fix_assignment_expression(self, line: str) -> str:
        """修复赋值表达式错误"""
        # 修复 = 应该是 == 的情况
        if ' = ' in line and any(keyword in line for keyword in ['if ', 'while ', 'elif ']):
            # 在条件语句中，= 应该是 ==
            line = re.sub(r'(\w+)\s*=\s*(\w+)', r'\1 == \2', line)
        
        return line
    
    def fix_invalid_syntax(self, line: str, line_num: int, lines: List[str]) -> str:
        """修复无效语法"""
        stripped = line.strip()
        
        # 修复常见的语法错误
        if stripped.startswith('def ') and not stripped.endswith(':'):
            if '(' in stripped and ')' in stripped:
                line = line.rstrip() + ':'
        
        # 修复空的函数体
        if (line_num > 0 and 
            lines[line_num - 1].strip().endswith(':') and 
            not stripped):
            current_indent = len(lines[line_num - 1]) - len(lines[line_num - 1].lstrip())
            return ' ' * (current_indent + 4) + 'pass'
        
        return line

def fix_grpc_files(service_path: Path):
    """修复gRPC生成的文件"""
    grpc_dir = service_path / "api" / "grpc"
    if not grpc_dir.exists():
        return
    
    logger.info("🔧 修复gRPC文件...")
    
    for grpc_file in grpc_dir.glob("*.py"):
        try:
            with open(grpc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 修复gRPC文件的常见问题
            lines = content.split('\n')
            fixed_lines = []
            
            for line in lines:
                # 修复意外的缩进
                if line.startswith('    ') and not any(prev_line.strip().endswith(':') for prev_line in fixed_lines[-3:] if prev_line.strip()):
                    line = line.lstrip()
                
                # 修复缩进不匹配
                if line.strip() and not line.startswith(' '):
                    # 检查是否应该有缩进
                    if fixed_lines and fixed_lines[-1].strip().endswith(':'):
                        line = '    ' + line
                
                fixed_lines.append(line)
            
            # 验证修复结果
            fixed_content = '\n'.join(fixed_lines)
            try:
                ast.parse(fixed_content)
                with open(grpc_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                logger.info(f"  ✅ 修复gRPC文件: {grpc_file.name}")
            except SyntaxError:
                logger.warning(f"  ⚠️ gRPC文件修复失败: {grpc_file.name}")
                
        except Exception as e:
            logger.error(f"处理gRPC文件 {grpc_file} 时出错: {e}")

def add_missing_pass_statements(service_path: Path):
    """为空的函数和类添加pass语句"""
    logger.info("🔧 添加缺失的pass语句...")
    
    for py_file in service_path.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            fixed_lines = []
            
            for i, line in enumerate(lines):
                fixed_lines.append(line)
                
                # 检查是否是函数或类定义
                if (line.strip().endswith(':') and 
                    any(keyword in line for keyword in ['def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except', 'with ', 'else:', 'elif '])):
                    
                    # 检查下一行是否为空或者是另一个定义
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        if (not next_line.strip() or 
                            (next_line.strip() and not next_line.startswith(' '))):
                            # 添加pass语句
                            current_indent = len(line) - len(line.lstrip())
                            pass_line = ' ' * (current_indent + 4) + 'pass'
                            fixed_lines.append(pass_line)
            
            # 验证并写入
            fixed_content = '\n'.join(fixed_lines)
            try:
                ast.parse(fixed_content)
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
            except SyntaxError:
                pass  # 如果还有错误，跳过
                
        except Exception as e:
            logger.error(f"处理文件 {py_file} 时出错: {e}")

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python comprehensive_syntax_fixer.py <service_path>")
        sys.exit(1)
    
    service_path = Path(sys.argv[1])
    if not service_path.exists():
        print(f"错误: 路径 {service_path} 不存在")
        sys.exit(1)
    
    # 创建修复器
    fixer = ComprehensiveSyntaxFixer(str(service_path))
    
    # 修复gRPC文件
    fix_grpc_files(service_path)
    
    # 添加缺失的pass语句
    add_missing_pass_statements(service_path)
    
    # 修复所有语法错误
    success = fixer.fix_all_syntax_errors()
    
    if success:
        logger.info("🎉 语法修复完成！")
    else:
        logger.warning("⚠️ 部分文件可能仍有语法错误")

if __name__ == "__main__":
    main() 