"""
code_quality_check - 索克生活项目模块
"""

from collections import defaultdict, Counter
from pathlib import Path
from typing import List, Dict, Set, Tuple
import argparse
import ast
import json
import os
import re

#!/usr/bin/env python3
"""
索克生活项目代码质量检查脚本
检查并清理冗余代码、未使用的导入、重复代码等
"""


class CodeQualityChecker:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)
        
    def check_python_files(self) -> Dict:
        """检查Python文件的代码质量"""
        print("🐍 检查Python文件...")
        
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        
        for py_file in python_files:
            try:
                self._check_python_file(py_file)
            except Exception as e:
                self.issues['python_errors'].append({
                    'file': str(py_file),
                    'error': str(e)
                })
        
        return {
            'total_files': len(python_files),
            'issues': dict(self.issues),
            'stats': dict(self.stats)
        }
    
    def check_javascript_files(self) -> Dict:
        """检查JavaScript/TypeScript文件的代码质量"""
        print("📱 检查JavaScript/TypeScript文件...")
        
        js_files = []
        for pattern in ["*.js", "*.jsx", "*.ts", "*.tsx"]:
            js_files.extend(self.project_root.rglob(pattern))
        
        js_files = [f for f in js_files if not self._should_skip_file(f)]
        
        for js_file in js_files:
            try:
                self._check_javascript_file(js_file)
            except Exception as e:
                self.issues['javascript_errors'].append({
                    'file': str(js_file),
                    'error': str(e)
                })
        
        return {
            'total_files': len(js_files),
            'issues': dict(self.issues),
            'stats': dict(self.stats)
        }
    
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
            'coverage'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def _check_python_file(self, file_path: Path):
        """检查单个Python文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content)
            
            # 检查未使用的导入
            self._check_unused_imports(file_path, tree, content)
            
            # 检查重复代码
            self._check_duplicate_code(file_path, content)
            
            # 检查代码复杂度
            self._check_complexity(file_path, tree)
            
            # 检查TODO和FIXME
            self._check_todos(file_path, content)
            
            self.stats['python_files_checked'] += 1
            
        except SyntaxError as e:
            self.issues['syntax_errors'].append({
                'file': str(file_path),
                'line': e.lineno,
                'error': str(e)
            })
    
    def _check_javascript_file(self, file_path: Path):
        """检查单个JavaScript/TypeScript文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查未使用的导入
            self._check_js_unused_imports(file_path, content)
            
            # 检查重复代码
            self._check_duplicate_code(file_path, content)
            
            # 检查TODO和FIXME
            self._check_todos(file_path, content)
            
            # 检查console.log
            self._check_console_logs(file_path, content)
            
            self.stats['js_files_checked'] += 1
            
        except Exception as e:
            self.issues['js_parse_errors'].append({
                'file': str(file_path),
                'error': str(e)
            })
    
    def _check_unused_imports(self, file_path: Path, tree: ast.AST, content: str):
        """检查未使用的Python导入"""
        imports = []
        used_names = set()
        
        # 收集导入
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append(alias.name if alias.name != '*' else None)
            elif isinstance(node, ast.Name):
                used_names.add(node.id)
        
        # 检查未使用的导入
        unused_imports = []
        for imp in imports:
            if imp and imp not in used_names:
                # 检查是否在字符串中使用
                if imp not in content:
                    unused_imports.append(imp)
        
        if unused_imports:
            self.issues['unused_imports'].append({
                'file': str(file_path),
                'imports': unused_imports
            })
            self.stats['unused_imports_count'] += len(unused_imports)
    
    def _check_js_unused_imports(self, file_path: Path, content: str):
        """检查未使用的JavaScript/TypeScript导入"""
        import_pattern = r'import\s+(?:{[^}]+}|\w+|\*\s+as\s+\w+)\s+from\s+[\'"][^\'"]+[\'"]'
        imports = re.findall(import_pattern, content)
        
        # 简单检查：如果导入的变量在代码中没有使用
        for imp in imports:
            # 提取导入的变量名
            if '{' in imp:
                # 解构导入
                match = re.search(r'{([^}]+)}', imp)
                if match:
                    vars_str = match.group(1)
                    vars_list = [v.strip().split(' as ')[-1] for v in vars_str.split(',')]
                    for var in vars_list:
                        var = var.strip()
                        if var and content.count(var) == 1:  # 只出现一次（在导入中）
                            self.issues['js_unused_imports'].append({
                                'file': str(file_path),
                                'import': var
                            })
    
    def _check_duplicate_code(self, file_path: Path, content: str):
        """检查重复代码"""
        lines = content.split('\n')
        line_counts = Counter(line.strip() for line in lines if line.strip())
        
        duplicates = {line: count for line, count in line_counts.items() 
                     if count > 3 and len(line) > 20}
        
        if duplicates:
            self.issues['duplicate_lines'].append({
                'file': str(file_path),
                'duplicates': duplicates
            })
            self.stats['duplicate_lines_count'] += len(duplicates)
    
    def _check_complexity(self, file_path: Path, tree: ast.AST):
        """检查代码复杂度"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = self._calculate_complexity(node)
                if complexity > 10:  # 复杂度阈值
                    self.issues['high_complexity'].append({
                        'file': str(file_path),
                        'function': node.name,
                        'complexity': complexity,
                        'line': node.lineno
                    })
                    self.stats['high_complexity_functions'] += 1
    
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
        
        return complexity
    
    def _check_todos(self, file_path: Path, content: str):
        """检查TODO和FIXME注释"""
        lines = content.split('\n')
        todos = []
        
        for i, line in enumerate(lines, 1):
            if re.search(r'(TODO|FIXME|XXX|HACK)', line, re.IGNORECASE):
                todos.append({
                    'line': i,
                    'content': line.strip()
                })
        
        if todos:
            self.issues['todos'].append({
                'file': str(file_path),
                'todos': todos
            })
            self.stats['todos_count'] += len(todos)
    
    def _check_console_logs(self, file_path: Path, content: str):
        """检查console.log语句"""
        console_logs = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if 'console.log' in line and not line.strip().startswith('//'):
                console_logs.append({
                    'line': i,
                    'content': line.strip()
                })
        
        if console_logs:
            self.issues['console_logs'].append({
                'file': str(file_path),
                'logs': console_logs
            })
            self.stats['console_logs_count'] += len(console_logs)
    
    def check_package_dependencies(self):
        """检查包依赖"""
        print("📦 检查包依赖...")
        
        # 检查package.json
        package_json = self.project_root / 'package.json'
        if package_json.exists():
            self._check_npm_dependencies(package_json)
        
        # 检查requirements.txt
        requirements_txt = self.project_root / 'requirements.txt'
        if requirements_txt.exists():
            self._check_python_dependencies(requirements_txt)
    
    def _check_npm_dependencies(self, package_json: Path):
        """检查npm依赖"""
        try:
            with open(package_json, 'r') as f:
                data = json.load(f)
            
            dependencies = data.get('dependencies', {})
            dev_dependencies = data.get('devDependencies', {})
            
            # 检查是否有重复的依赖
            common_deps = set(dependencies.keys()) & set(dev_dependencies.keys())
            if common_deps:
                self.issues['duplicate_dependencies'].append({
                    'file': str(package_json),
                    'duplicates': list(common_deps)
                })
            
            self.stats['npm_dependencies'] = len(dependencies)
            self.stats['npm_dev_dependencies'] = len(dev_dependencies)
            
        except Exception as e:
            self.issues['package_json_errors'].append({
                'file': str(package_json),
                'error': str(e)
            })
    
    def _check_python_dependencies(self, requirements_txt: Path):
        """检查Python依赖"""
        try:
            with open(requirements_txt, 'r') as f:
                lines = f.readlines()
            
            deps = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    dep_name = line.split('==')[0].split('>=')[0].split('<=')[0]
                    deps.append(dep_name)
            
            # 检查重复依赖
            dep_counts = Counter(deps)
            duplicates = {dep: count for dep, count in dep_counts.items() if count > 1}
            
            if duplicates:
                self.issues['duplicate_python_deps'].append({
                    'file': str(requirements_txt),
                    'duplicates': duplicates
                })
            
            self.stats['python_dependencies'] = len(set(deps))
            
        except Exception as e:
            self.issues['requirements_errors'].append({
                'file': str(requirements_txt),
                'error': str(e)
            })
    
    def generate_report(self) -> str:
        """生成清理报告"""
        report = f"""# 🔍 代码质量检查报告

**检查时间**: {os.popen('date').read().strip()}
**项目路径**: {self.project_root}

## 📊 统计信息

- Python文件检查: {self.stats.get('python_files_checked', 0)} 个
- JavaScript/TypeScript文件检查: {self.stats.get('js_files_checked', 0)} 个
- 未使用导入: {self.stats.get('unused_imports_count', 0)} 个
- 重复代码行: {self.stats.get('duplicate_lines_count', 0)} 个
- 高复杂度函数: {self.stats.get('high_complexity_functions', 0)} 个
- TODO注释: {self.stats.get('todos_count', 0)} 个
- Console.log语句: {self.stats.get('console_logs_count', 0)} 个

## 🚨 发现的问题

"""
        
        # 添加各类问题的详细信息
        for issue_type, issues in self.issues.items():
            if issues:
                report += f"\n### {issue_type.replace('_', ' ').title()}\n\n"
                for issue in issues[:5]:  # 只显示前5个
                    report += f"- **{issue.get('file', 'Unknown')}**\n"
                    if 'imports' in issue:
                        report += f"  - 未使用导入: {', '.join(issue['imports'])}\n"
                    elif 'duplicates' in issue:
                        report += f"  - 重复项: {len(issue['duplicates'])} 个\n"
                    elif 'complexity' in issue:
                        report += f"  - 函数: {issue['function']}, 复杂度: {issue['complexity']}\n"
                    elif 'todos' in issue:
                        report += f"  - TODO数量: {len(issue['todos'])}\n"
                    elif 'logs' in issue:
                        report += f"  - Console.log数量: {len(issue['logs'])}\n"
                
                if len(issues) > 5:
                    report += f"\n... 还有 {len(issues) - 5} 个类似问题\n"
        
        report += f"""

## 🎯 建议的清理操作

1. **清理未使用的导入**: 删除 {self.stats.get('unused_imports_count', 0)} 个未使用的导入
2. **重构重复代码**: 提取 {self.stats.get('duplicate_lines_count', 0)} 处重复代码为函数
3. **降低复杂度**: 重构 {self.stats.get('high_complexity_functions', 0)} 个高复杂度函数
4. **清理调试代码**: 删除 {self.stats.get('console_logs_count', 0)} 个console.log语句
5. **处理TODO**: 完成或删除 {self.stats.get('todos_count', 0)} 个TODO注释

## 🔧 自动修复建议

```bash
# 使用工具自动修复
npm run lint:fix  # 修复JavaScript/TypeScript问题
autopep8 --in-place --recursive .  # 修复Python格式问题
isort .  # 排序Python导入
```

## 📈 代码质量评分

总体评分: {self._calculate_quality_score()}/100

"""
        
        return report
    
    def _calculate_quality_score(self) -> int:
        """计算代码质量评分"""
        total_files = self.stats.get('python_files_checked', 0) + self.stats.get('js_files_checked', 0)
        if total_files == 0:
            return 100
        
        # 基础分数
        score = 100
        
        # 扣分项
        score -= min(self.stats.get('unused_imports_count', 0) * 2, 20)
        score -= min(self.stats.get('duplicate_lines_count', 0), 15)
        score -= min(self.stats.get('high_complexity_functions', 0) * 5, 25)
        score -= min(self.stats.get('console_logs_count', 0), 10)
        score -= min(len(self.issues.get('syntax_errors', [])) * 10, 30)
        
        return max(score, 0)

def main():
    parser = argparse.ArgumentParser(description='索克生活项目代码质量检查')
    parser.add_argument('--project-root', default='.', help='项目根目录路径')
    parser.add_argument('--output', default='code_quality_report.md', help='输出报告文件名')
    
    args = parser.parse_args()
    
    print("🔍 开始代码质量检查...")
    
    checker = CodeQualityChecker(args.project_root)
    
    # 执行检查
    checker.check_python_files()
    checker.check_javascript_files()
    checker.check_package_dependencies()
    
    # 生成报告
    report = checker.generate_report()
    
    # 保存报告
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 代码质量检查完成！报告已保存到: {args.output}")
    print(f"📊 代码质量评分: {checker._calculate_quality_score()}/100")

if __name__ == '__main__':
    main() 