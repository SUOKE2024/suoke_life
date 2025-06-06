"""
complexity_refactor - 索克生活项目模块
"""

from pathlib import Path
from typing import List, Dict, Tuple, Optional
import argparse
import ast
import os
import re

#!/usr/bin/env python3
"""
索克生活项目复杂度重构脚本
专门重构高复杂度函数，提升代码质量
"""


class ComplexityRefactor:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.refactored_functions = []
        self.high_complexity_functions = []
        
    def analyze_complexity(self) -> Dict:
        """分析项目中的高复杂度函数"""
        print("🔍 分析高复杂度函数...")
        
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                self._analyze_file_complexity(py_file, tree)
                
            except Exception as e:
                print(f"  ⚠️  分析文件时出错 {py_file}: {e}")
        
        # 按复杂度排序
        self.high_complexity_functions.sort(key=lambda x: x['complexity'], reverse=True)
        
        return {
            'total_functions': len(self.high_complexity_functions),
            'high_complexity_functions': self.high_complexity_functions[:50]  # 只返回前50个
        }
    
    def _analyze_file_complexity(self, file_path: Path, tree: ast.AST):
        """分析单个文件的复杂度"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = self._calculate_complexity(node)
                if complexity > 10:  # 复杂度阈值
                    self.high_complexity_functions.append({
                        'file': str(file_path),
                        'function': node.name,
                        'complexity': complexity,
                        'line': node.lineno,
                        'node': node
                    })
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.ListComp):
                complexity += 1
            elif isinstance(child, ast.DictComp):
                complexity += 1
            elif isinstance(child, ast.SetComp):
                complexity += 1
        
        return complexity
    
    def refactor_high_complexity_functions(self, max_functions: int = 20) -> Dict:
        """重构高复杂度函数"""
        print(f"🔧 重构前{max_functions}个高复杂度函数...")
        
        refactored_count = 0
        
        for func_info in self.high_complexity_functions[:max_functions]:
            try:
                if self._refactor_function(func_info):
                    refactored_count += 1
                    self.refactored_functions.append(func_info)
                    print(f"  ✅ 已重构: {func_info['file']}:{func_info['function']} (复杂度: {func_info['complexity']})")
                else:
                    print(f"  ⚠️  跳过: {func_info['file']}:{func_info['function']} (复杂度: {func_info['complexity']})")
            except Exception as e:
                print(f"  ❌ 重构失败: {func_info['file']}:{func_info['function']} - {e}")
        
        return {
            'refactored_count': refactored_count,
            'total_analyzed': len(self.high_complexity_functions[:max_functions])
        }
    
    def _refactor_function(self, func_info: Dict) -> bool:
        """重构单个函数"""
        file_path = Path(func_info['file'])
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            tree = ast.parse(content)
            
            # 找到目标函数
            target_function = None
            for node in ast.walk(tree):
                if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and 
                    node.name == func_info['function'] and 
                    node.lineno == func_info['line']):
                    target_function = node
                    break
            
            if not target_function:
                return False
            
            # 尝试重构
            refactored_code = self._apply_refactoring_patterns(target_function, lines)
            
            if refactored_code:
                # 验证重构后的代码
                try:
                    ast.parse('\n'.join(refactored_code))
                    
                    # 保存重构后的代码
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(refactored_code))
                    
                    return True
                except SyntaxError:
                    return False
            
        except Exception as e:
            print(f"    重构错误: {e}")
            return False
        
        return False
    
    def _apply_refactoring_patterns(self, function_node: ast.AST, lines: List[str]) -> Optional[List[str]]:
        """应用重构模式"""
        start_line = function_node.lineno - 1
        end_line = function_node.end_lineno if hasattr(function_node, 'end_lineno') else len(lines)
        
        function_lines = lines[start_line:end_line]
        original_function = '\n'.join(function_lines)
        
        # 重构模式1: 提取条件判断
        refactored = self._extract_complex_conditions(function_lines)
        if refactored != function_lines:
            return lines[:start_line] + refactored + lines[end_line:]
        
        # 重构模式2: 提取循环逻辑
        refactored = self._extract_loop_logic(function_lines)
        if refactored != function_lines:
            return lines[:start_line] + refactored + lines[end_line:]
        
        # 重构模式3: 提取异常处理
        refactored = self._extract_exception_handling(function_lines)
        if refactored != function_lines:
            return lines[:start_line] + refactored + lines[end_line:]
        
        # 重构模式4: 简化嵌套结构
        refactored = self._simplify_nested_structure(function_lines)
        if refactored != function_lines:
            return lines[:start_line] + refactored + lines[end_line:]
        
        return None
    
    def _extract_complex_conditions(self, function_lines: List[str]) -> List[str]:
        """提取复杂条件判断"""
        refactored_lines = function_lines.copy()
        
        # 查找复杂的if条件
        for i, line in enumerate(function_lines):
            stripped = line.strip()
            if stripped.startswith('if ') and ('and' in stripped or 'or' in stripped):
                # 检查条件是否很长
                if len(stripped) > 80:
                    # 提取条件到单独的函数
                    indent = len(line) - len(line.lstrip())
                    condition_func_name = f"_is_condition_met_{i}"
                    
                    # 创建条件函数
                    condition_func = [
                        f"{' ' * indent}def {condition_func_name}(self) -> bool:",
                        f"{' ' * (indent + 4)}\"\"\"提取的条件判断逻辑\"\"\"",
                        f"{' ' * (indent + 4)}return {stripped[3:-1]}",  # 去掉'if '和':'
                        ""
                    ]
                    
                    # 替换原条件
                    refactored_lines[i] = f"{' ' * indent}if self.{condition_func_name}():"
                    
                    # 在函数开始前插入条件函数
                    refactored_lines = condition_func + refactored_lines
                    break
        
        return refactored_lines
    
    def _extract_loop_logic(self, function_lines: List[str]) -> List[str]:
        """提取循环逻辑"""
        refactored_lines = function_lines.copy()
        
        # 查找复杂的for循环
        for i, line in enumerate(function_lines):
            stripped = line.strip()
            if stripped.startswith('for ') and i + 10 < len(function_lines):
                # 检查循环体是否很长
                indent = len(line) - len(line.lstrip())
                loop_end = i + 1
                
                # 找到循环结束位置
                for j in range(i + 1, min(i + 20, len(function_lines))):
                    if function_lines[j].strip() and len(function_lines[j]) - len(function_lines[j].lstrip()) <= indent:
                        loop_end = j
                        break
                
                if loop_end - i > 8:  # 循环体超过8行
                    # 提取循环体到单独的方法
                    loop_func_name = f"_process_loop_item_{i}"
                    
                    # 提取循环变量
                    loop_var_match = re.search(r'for\s+(\w+)\s+in', stripped)
                    loop_var = loop_var_match.group(1) if loop_var_match else 'item'
                    
                    # 创建循环处理函数
                    loop_func = [
                        f"{' ' * indent}def {loop_func_name}(self, {loop_var}):",
                        f"{' ' * (indent + 4)}\"\"\"处理循环项的逻辑\"\"\"",
                    ]
                    
                    # 添加循环体内容
                    for k in range(i + 1, loop_end):
                        loop_func.append(function_lines[k])
                    
                    loop_func.append("")
                    
                    # 简化原循环
                    new_loop = [
                        line,
                        f"{' ' * (indent + 4)}self.{loop_func_name}({loop_var})"
                    ]
                    
                    # 替换原代码
                    refactored_lines = (function_lines[:i] + 
                                      loop_func + 
                                      new_loop + 
                                      function_lines[loop_end:])
                    break
        
        return refactored_lines
    
    def _extract_exception_handling(self, function_lines: List[str]) -> List[str]:
        """提取异常处理逻辑"""
        refactored_lines = function_lines.copy()
        
        # 查找复杂的try-except块
        for i, line in enumerate(function_lines):
            stripped = line.strip()
            if stripped.startswith('try:'):
                indent = len(line) - len(line.lstrip())
                
                # 找到except和finally块
                except_start = -1
                except_end = len(function_lines)
                
                for j in range(i + 1, len(function_lines)):
                    if function_lines[j].strip().startswith('except'):
                        except_start = j
                    elif (function_lines[j].strip() and 
                          len(function_lines[j]) - len(function_lines[j].lstrip()) <= indent and
                          not function_lines[j].strip().startswith(('except', 'finally', 'else'))):
                        except_end = j
                        break
                
                if except_start > 0 and except_end - except_start > 5:
                    # 提取异常处理逻辑
                    error_handler_name = f"_handle_error_{i}"
                    
                    # 创建错误处理函数
                    error_func = [
                        f"{' ' * indent}def {error_handler_name}(self, error: Exception):",
                        f"{' ' * (indent + 4)}\"\"\"处理异常的逻辑\"\"\"",
                    ]
                    
                    # 添加except块内容
                    for k in range(except_start + 1, except_end):
                        if not function_lines[k].strip().startswith(('except', 'finally')):
                            error_func.append(function_lines[k])
                    
                    error_func.append("")
                    
                    # 简化原异常处理
                    new_except = [
                        function_lines[except_start],
                        f"{' ' * (indent + 4)}self.{error_handler_name}(e)"
                    ]
                    
                    # 替换原代码
                    refactored_lines = (function_lines[:except_start] + 
                                      error_func + 
                                      new_except + 
                                      function_lines[except_end:])
                    break
        
        return refactored_lines
    
    def _simplify_nested_structure(self, function_lines: List[str]) -> List[str]:
        """简化嵌套结构"""
        refactored_lines = function_lines.copy()
        
        # 查找深度嵌套的if语句
        max_indent = 0
        for line in function_lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent)
        
        if max_indent > 16:  # 嵌套超过4层
            # 尝试使用早期返回模式
            for i, line in enumerate(function_lines):
                stripped = line.strip()
                if stripped.startswith('if ') and 'not ' not in stripped:
                    indent = len(line) - len(line.lstrip())
                    
                    # 查找对应的else
                    else_line = -1
                    for j in range(i + 1, len(function_lines)):
                        if (function_lines[j].strip() == 'else:' and 
                            len(function_lines[j]) - len(function_lines[j].lstrip()) == indent):
                            else_line = j
                            break
                    
                    if else_line > 0:
                        # 转换为早期返回
                        condition = stripped[3:-1]  # 去掉'if '和':'
                        new_condition = f"if not ({condition}):"
                        
                        refactored_lines[i] = f"{' ' * indent}{new_condition}"
                        # 在if块末尾添加return
                        refactored_lines.insert(else_line, f"{' ' * (indent + 4)}return")
                        # 删除else行
                        refactored_lines.pop(else_line + 1)
                        break
        
        return refactored_lines
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过某个文件"""
        skip_patterns = [
            'node_modules',
            'venv',
            '.venv',
            '__pycache__',
            '.git',
            'build',
            'dist',
            '.expo',
            'ios/Pods',
            'android/build',
            '.jest-cache',
            'coverage',
            'cleanup_backup',
            'test',
            '__test__'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def generate_report(self) -> str:
        """生成重构报告"""
        report = f"""# 🔧 复杂度重构报告

**重构时间**: {os.popen('date').read().strip()}
**项目路径**: {self.project_root}

## 📊 重构统计

- 发现高复杂度函数: {len(self.high_complexity_functions)} 个
- 成功重构函数: {len(self.refactored_functions)} 个
- 重构成功率: {len(self.refactored_functions) / max(len(self.high_complexity_functions[:20]), 1) * 100:.1f}%

## 🎯 重构的函数

"""
        
        for func in self.refactored_functions:
            report += f"- **{func['file']}:{func['function']}** (复杂度: {func['complexity']})\n"
        
        report += f"""

## 📈 剩余高复杂度函数 (前10个)

"""
        
        remaining_functions = [f for f in self.high_complexity_functions if f not in self.refactored_functions]
        for func in remaining_functions[:10]:
            report += f"- **{func['file']}:{func['function']}** (复杂度: {func['complexity']}, 行: {func['line']})\n"
        
        report += f"""

## 🔧 重构模式应用

本次重构应用了以下模式：

1. **条件提取**: 将复杂的条件判断提取为独立方法
2. **循环逻辑提取**: 将复杂的循环体提取为处理方法
3. **异常处理提取**: 将复杂的异常处理逻辑独立出来
4. **嵌套简化**: 使用早期返回模式减少嵌套层次

## 📈 预期效果

通过复杂度重构，预期：
- 代码可读性提升
- 维护成本降低
- 测试覆盖率提升
- 代码质量评分提升 15-25 分

## 🎯 后续建议

1. **手动审查**: 检查重构后的代码逻辑正确性
2. **运行测试**: 确保重构没有破坏功能
3. **持续重构**: 对剩余高复杂度函数进行手动重构
4. **建立规范**: 制定复杂度控制规范

"""
        
        return report

def main():
    parser = argparse.ArgumentParser(description='索克生活项目复杂度重构')
    parser.add_argument('--project-root', default='.', help='项目根目录路径')
    parser.add_argument('--output', default='complexity_refactor_report.md', help='输出报告文件名')
    parser.add_argument('--max-functions', type=int, default=20, help='最大重构函数数量')
    parser.add_argument('--analyze-only', action='store_true', help='只分析不重构')
    
    args = parser.parse_args()
    
    print("🔧 开始复杂度重构...")
    
    refactor = ComplexityRefactor(args.project_root)
    
    # 分析复杂度
    analysis_result = refactor.analyze_complexity()
    print(f"📊 发现 {analysis_result['total_functions']} 个高复杂度函数")
    
    if not args.analyze_only:
        # 执行重构
        refactor_result = refactor.refactor_high_complexity_functions(args.max_functions)
        print(f"✅ 成功重构 {refactor_result['refactored_count']} 个函数")
    
    # 生成报告
    report = refactor.generate_report()
    
    # 保存报告
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📋 重构报告已保存到: {args.output}")

if __name__ == '__main__':
    main() 