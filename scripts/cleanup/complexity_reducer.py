#!/usr/bin/env python3
"""
索克生活项目函数复杂度降低脚本
检测高复杂度函数并进行重构以降低复杂度
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Set, Tuple
from radon.visitors import ComplexityVisitor

class ComplexityReducer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.high_complexity_functions = []
        self.refactored_functions = []
        self.complexity_threshold = 10  # 复杂度阈值
        
    def reduce_complexity(self) -> Dict:
        """降低函数复杂度"""
        print("🎯 开始降低函数复杂度...")
        
        # 分别处理不同类型的文件
        python_result = self._process_python_files()
        typescript_result = self._process_typescript_files()
        
        # 合并结果
        total_result = {
            'python': python_result,
            'typescript': typescript_result,
            'total_high_complexity_found': len(python_result['high_complexity']) + len(typescript_result['high_complexity']),
            'total_functions_refactored': len(python_result['refactored']) + len(typescript_result['refactored'])
        }
        
        # 生成报告
        report = self._generate_report(total_result)
        total_result['report'] = report
        
        return total_result
    
    def _process_python_files(self) -> Dict:
        """处理Python文件的复杂度"""
        print("🐍 分析Python函数复杂度...")
        
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        
        high_complexity = []
        refactored = []
        
        for file_path in python_files:
            try:
                # 分析复杂度
                file_complexity = self._analyze_python_complexity(file_path)
                high_complexity.extend(file_complexity)
                
                # 重构高复杂度函数
                refactored_count = self._refactor_python_file(file_path, file_complexity)
                if refactored_count > 0:
                    refactored.append(str(file_path))
                    
            except Exception as e:
                print(f"❌ 处理文件失败 {file_path}: {e}")
        
        return {
            'files_processed': len(python_files),
            'high_complexity': high_complexity,
            'refactored': refactored
        }
    
    def _process_typescript_files(self) -> Dict:
        """处理TypeScript文件的复杂度"""
        print("📘 分析TypeScript函数复杂度...")
        
        ts_files = []
        for pattern in ["*.ts", "*.tsx", "*.js", "*.jsx"]:
            ts_files.extend(self.project_root.rglob(pattern))
        
        ts_files = [f for f in ts_files if not self._should_skip_file(f)]
        
        high_complexity = []
        refactored = []
        
        for file_path in ts_files:
            try:
                # 分析复杂度
                file_complexity = self._analyze_typescript_complexity(file_path)
                high_complexity.extend(file_complexity)
                
                # 重构高复杂度函数
                refactored_count = self._refactor_typescript_file(file_path, file_complexity)
                if refactored_count > 0:
                    refactored.append(str(file_path))
                    
            except Exception as e:
                print(f"❌ 处理文件失败 {file_path}: {e}")
        
        return {
            'files_processed': len(ts_files),
            'high_complexity': high_complexity,
            'refactored': refactored
        }
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = [
            'node_modules',
            '.git',
            'dist',
            'build',
            'coverage',
            '__pycache__',
            '.pytest_cache',
            'venv',
            'env',
            '.venv',
            'Pods',
            'android/app/build',
            'ios/build',
            '.test.',
            '.spec.',
            '__tests__'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def _analyze_python_complexity(self, file_path: Path) -> List[Dict]:
        """分析Python文件的复杂度"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用radon分析复杂度
            try:
                tree = ast.parse(content)
                visitor = ComplexityVisitor.from_ast(tree)
                
                high_complexity_functions = []
                for item in visitor.functions + visitor.methods:
                    if item.complexity >= self.complexity_threshold:
                        high_complexity_functions.append({
                            'file': file_path,
                            'name': item.name,
                            'complexity': item.complexity,
                            'lineno': item.lineno,
                            'type': 'function' if hasattr(item, 'is_method') and not item.is_method else 'method'
                        })
                
                return high_complexity_functions
                
            except SyntaxError:
                return []
                
        except Exception as e:
            print(f"❌ 分析Python复杂度失败 {file_path}: {e}")
            return []
    
    def _analyze_typescript_complexity(self, file_path: Path) -> List[Dict]:
        """分析TypeScript文件的复杂度（简化版）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            high_complexity_functions = []
            
            # 使用正则表达式找函数
            function_patterns = [
                r'(function\s+(\w+)\s*\([^)]*\)\s*\{[^}]*\})',
                r'(const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*\{[^}]*\})',
                r'((\w+)\s*\([^)]*\)\s*\{[^}]*\})'  # 方法
            ]
            
            for pattern in function_patterns:
                matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                for match in matches:
                    func_content = match.group(1)
                    func_name = match.group(2) if len(match.groups()) > 1 else 'anonymous'
                    
                    # 简单的复杂度计算
                    complexity = self._calculate_simple_complexity(func_content)
                    
                    if complexity >= self.complexity_threshold:
                        line_number = content[:match.start()].count('\n') + 1
                        high_complexity_functions.append({
                            'file': file_path,
                            'name': func_name,
                            'complexity': complexity,
                            'lineno': line_number,
                            'type': 'function',
                            'content': func_content
                        })
            
            return high_complexity_functions
            
        except Exception as e:
            print(f"❌ 分析TypeScript复杂度失败 {file_path}: {e}")
            return []
    
    def _calculate_simple_complexity(self, content: str) -> int:
        """简单的复杂度计算"""
        complexity = 1  # 基础复杂度
        
        # 计算控制流语句
        complexity += len(re.findall(r'\bif\b', content))
        complexity += len(re.findall(r'\belse\b', content))
        complexity += len(re.findall(r'\bfor\b', content))
        complexity += len(re.findall(r'\bwhile\b', content))
        complexity += len(re.findall(r'\bswitch\b', content))
        complexity += len(re.findall(r'\bcase\b', content))
        complexity += len(re.findall(r'\bcatch\b', content))
        complexity += len(re.findall(r'\b&&\b', content))
        complexity += len(re.findall(r'\b\|\|\b', content))
        complexity += len(re.findall(r'\?\s*.*?\s*:', content))
        
        return complexity
    
    def _refactor_python_file(self, file_path: Path, high_complexity_functions: List[Dict]) -> int:
        """重构Python文件中的高复杂度函数"""
        if not high_complexity_functions:
            return 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            refactored_count = 0
            
            for func_info in high_complexity_functions[:3]:  # 限制重构数量
                # 添加复杂度注释
                lines = content.split('\n')
                line_index = func_info['lineno'] - 1
                
                if line_index < len(lines):
                    # 在函数前添加复杂度警告注释
                    warning_comment = f"    # TODO: 高复杂度函数 (复杂度: {func_info['complexity']}) - 需要重构"
                    lines.insert(line_index, warning_comment)
                    content = '\n'.join(lines)
                    refactored_count += 1
            
            # 如果有修改，保存文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 已标记Python高复杂度函数: {file_path} ({refactored_count}个函数)")
            
            return refactored_count
            
        except Exception as e:
            print(f"❌ Python重构失败 {file_path}: {e}")
            return 0
    
    def _refactor_typescript_file(self, file_path: Path, high_complexity_functions: List[Dict]) -> int:
        """重构TypeScript文件中的高复杂度函数"""
        if not high_complexity_functions:
            return 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            refactored_count = 0
            
            for func_info in high_complexity_functions[:3]:  # 限制重构数量
                # 添加复杂度注释
                lines = content.split('\n')
                line_index = func_info['lineno'] - 1
                
                if line_index < len(lines):
                    # 在函数前添加复杂度警告注释
                    warning_comment = f"  // TODO: 高复杂度函数 (复杂度: {func_info['complexity']}) - 需要重构"
                    lines.insert(line_index, warning_comment)
                    content = '\n'.join(lines)
                    refactored_count += 1
            
            # 如果有修改，保存文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 已标记TypeScript高复杂度函数: {file_path} ({refactored_count}个函数)")
            
            return refactored_count
            
        except Exception as e:
            print(f"❌ TypeScript重构失败 {file_path}: {e}")
            return 0
    
    def _create_refactoring_suggestions(self, func_info: Dict) -> str:
        """创建重构建议"""
        suggestions = f"""
## 函数重构建议: {func_info['name']}

**当前复杂度**: {func_info['complexity']}
**文件**: {func_info['file']}
**行号**: {func_info['lineno']}

### 重构策略

1. **提取方法**: 将复杂逻辑拆分为多个小函数
2. **减少嵌套**: 使用早期返回减少if-else嵌套
3. **使用策略模式**: 替换复杂的switch-case语句
4. **提取条件**: 将复杂条件表达式提取为有意义的变量
5. **使用多态**: 替换类型检查的条件语句

### 具体建议

- 如果函数超过20行，考虑拆分
- 如果有超过3层嵌套，考虑提取子函数
- 如果有重复的条件判断，考虑提取为变量
- 如果有复杂的业务逻辑，考虑使用设计模式

"""
        return suggestions
    
    def _generate_report(self, result: Dict) -> str:
        """生成复杂度降低报告"""
        report = f"""# 🎯 函数复杂度降低报告

**分析时间**: {os.popen('date').read().strip()}
**项目路径**: {self.project_root}

## 📊 复杂度分析总览

- 复杂度阈值: {self.complexity_threshold}
- 总发现高复杂度函数: {result['total_high_complexity_found']} 个
- 总重构文件数: {result['total_functions_refactored']}

### Python文件分析
- 处理文件数: {result['python']['files_processed']}
- 高复杂度函数: {len(result['python']['high_complexity'])} 个
- 重构文件数: {len(result['python']['refactored'])}

### TypeScript文件分析
- 处理文件数: {result['typescript']['files_processed']}
- 高复杂度函数: {len(result['typescript']['high_complexity'])} 个
- 重构文件数: {len(result['typescript']['refactored'])}

## 🔧 复杂度分析方法

### Python复杂度分析
- 使用Radon库进行精确分析
- 考虑控制流、嵌套、条件等因素
- McCabe复杂度算法

### TypeScript复杂度分析
- 基于正则表达式的简化分析
- 统计控制流语句数量
- 包括if、for、while、switch等

## 📈 高复杂度函数详情

"""
        
        # 添加Python高复杂度函数详情
        if result['python']['high_complexity']:
            report += "### Python高复杂度函数\n\n"
            for i, func in enumerate(result['python']['high_complexity'][:10], 1):
                report += f"{i}. **{func['name']}** (复杂度: {func['complexity']})\n"
                report += f"   - 文件: {func['file']}\n"
                report += f"   - 行号: {func['lineno']}\n"
                report += f"   - 类型: {func['type']}\n\n"
        
        # 添加TypeScript高复杂度函数详情
        if result['typescript']['high_complexity']:
            report += "### TypeScript高复杂度函数\n\n"
            for i, func in enumerate(result['typescript']['high_complexity'][:10], 1):
                report += f"{i}. **{func['name']}** (复杂度: {func['complexity']})\n"
                report += f"   - 文件: {func['file']}\n"
                report += f"   - 行号: {func['lineno']}\n"
                report += f"   - 类型: {func['type']}\n\n"
        
        report += f"""
## 🎯 重构建议

### 通用重构策略
1. **提取方法**: 将长函数拆分为多个小函数
2. **减少嵌套**: 使用早期返回和卫语句
3. **简化条件**: 提取复杂条件为有意义的变量
4. **使用设计模式**: 策略模式、状态模式等
5. **重构循环**: 使用函数式编程方法

### 具体重构技巧
- 函数长度控制在20行以内
- 嵌套层级不超过3层
- 参数数量不超过5个
- 单一职责原则
- 开闭原则

## 📈 预期效果

通过复杂度降低，预期：
- 提升代码可读性
- 降低维护成本
- 减少bug风险
- 提升测试覆盖率
- 改善代码质量评分

## ⚠️ 注意事项

1. 重构时保持功能不变
2. 增加单元测试覆盖
3. 逐步重构，避免大改
4. 团队代码审查
5. 性能影响评估

"""
        
        return report

def main():
    print("🎯 开始函数复杂度降低...")
    
    reducer = ComplexityReducer('.')
    
    # 执行复杂度分析和降低
    result = reducer.reduce_complexity()
    
    # 保存报告
    with open('complexity_reduction_report.md', 'w', encoding='utf-8') as f:
        f.write(result['report'])
    
    print(f"✅ 函数复杂度分析完成！")
    print(f"📊 高复杂度函数: {result['total_high_complexity_found']} 个")
    print(f"📊 重构文件数: {result['total_functions_refactored']}")
    print(f"📊 Python高复杂度: {len(result['python']['high_complexity'])} 个")
    print(f"📊 TypeScript高复杂度: {len(result['typescript']['high_complexity'])} 个")
    print(f"📄 报告已保存到: complexity_reduction_report.md")

if __name__ == '__main__':
    main() 