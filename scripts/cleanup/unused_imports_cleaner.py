#!/usr/bin/env python3
"""
索克生活项目未使用导入清理脚本
清理所有未使用的import语句
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Set, Tuple

class UnusedImportsCleaner:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.cleaned_files = []
        
    def clean_unused_imports(self) -> Dict:
        """清理所有未使用的导入"""
        print("🧹 开始清理未使用的导入...")
        
        # 分别处理Python和TypeScript文件
        python_result = self._clean_python_imports()
        typescript_result = self._clean_typescript_imports()
        
        # 合并结果
        total_result = {
            'python': python_result,
            'typescript': typescript_result,
            'total_files_cleaned': python_result['files_cleaned'] + typescript_result['files_cleaned'],
            'total_imports_removed': python_result['imports_removed'] + typescript_result['imports_removed']
        }
        
        # 生成报告
        report = self._generate_report(total_result)
        total_result['report'] = report
        
        return total_result
    
    def _clean_python_imports(self) -> Dict:
        """清理Python文件的未使用导入"""
        print("🐍 清理Python未使用导入...")
        
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        
        files_cleaned = 0
        imports_removed = 0
        
        for file_path in python_files:
            removed_count = self._clean_python_file_imports(file_path)
            if removed_count > 0:
                files_cleaned += 1
                imports_removed += removed_count
        
        return {
            'files_processed': len(python_files),
            'files_cleaned': files_cleaned,
            'imports_removed': imports_removed
        }
    
    def _clean_typescript_imports(self) -> Dict:
        """清理TypeScript文件的未使用导入"""
        print("📘 清理TypeScript未使用导入...")
        
        ts_files = []
        for pattern in ["*.ts", "*.tsx", "*.js", "*.jsx"]:
            ts_files.extend(self.project_root.rglob(pattern))
        
        ts_files = [f for f in ts_files if not self._should_skip_file(f)]
        
        files_cleaned = 0
        imports_removed = 0
        
        for file_path in ts_files:
            removed_count = self._clean_typescript_file_imports(file_path)
            if removed_count > 0:
                files_cleaned += 1
                imports_removed += removed_count
        
        return {
            'files_processed': len(ts_files),
            'files_cleaned': files_cleaned,
            'imports_removed': imports_removed
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
            '__init__.py'  # 保留__init__.py文件的导入
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def _clean_python_file_imports(self, file_path: Path) -> int:
        """清理Python文件的未使用导入"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return 0
            
            # 收集所有导入和使用的名称
            imports = self._collect_python_imports(tree)
            used_names = self._collect_python_used_names(tree)
            
            # 找出未使用的导入
            unused_imports = []
            for imp in imports:
                if not any(name in used_names for name in imp['names']):
                    unused_imports.append(imp)
            
            if not unused_imports:
                return 0
            
            # 移除未使用的导入
            lines = content.split('\n')
            lines_to_remove = set()
            
            for imp in unused_imports:
                lines_to_remove.add(imp['line_number'] - 1)  # AST行号从1开始
            
            # 重建文件内容
            new_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
            new_content = '\n'.join(new_lines)
            
            # 清理多余的空行
            new_content = re.sub(r'\n\s*\n\s*\n', '\n\n', new_content)
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Python文件已清理 {len(unused_imports)} 个未使用导入: {file_path}")
            return len(unused_imports)
            
        except Exception as e:
            print(f"❌ Python文件清理失败 {file_path}: {e}")
            return 0
    
    def _clean_typescript_file_imports(self, file_path: Path) -> int:
        """清理TypeScript文件的未使用导入"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 使用正则表达式找出导入语句
            import_patterns = [
                r'import\s+\{[^}]*\}\s+from\s+[\'"][^\'"]*[\'"];?\s*\n?',
                r'import\s+\*\s+as\s+\w+\s+from\s+[\'"][^\'"]*[\'"];?\s*\n?',
                r'import\s+\w+\s+from\s+[\'"][^\'"]*[\'"];?\s*\n?',
                r'import\s+[\'"][^\'"]*[\'"];?\s*\n?'
            ]
            
            removed_count = 0
            
            # 简单的启发式方法：如果导入的名称在文件中没有被使用，则移除
            for pattern in import_patterns:
                imports = re.findall(pattern, content, re.MULTILINE)
                for imp in imports:
                    # 提取导入的名称
                    imported_names = self._extract_typescript_import_names(imp)
                    
                    # 检查是否被使用（简单的字符串搜索）
                    is_used = False
                    for name in imported_names:
                        if name and re.search(rf'\b{re.escape(name)}\b', content.replace(imp, '')):
                            is_used = True
                            break
                    
                    if not is_used and imported_names:
                        content = content.replace(imp, '')
                        removed_count += 1
            
            # 清理多余的空行
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ TypeScript文件已清理 {removed_count} 个未使用导入: {file_path}")
                return removed_count
            
            return 0
            
        except Exception as e:
            print(f"❌ TypeScript文件清理失败 {file_path}: {e}")
            return 0
    
    def _collect_python_imports(self, tree: ast.AST) -> List[Dict]:
        """收集Python文件中的所有导入"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
                imports.append({
                    'type': 'import',
                    'names': names,
                    'line_number': node.lineno
                })
            elif isinstance(node, ast.ImportFrom):
                names = [alias.name for alias in node.names] if node.names else []
                imports.append({
                    'type': 'from_import',
                    'module': node.module,
                    'names': names,
                    'line_number': node.lineno
                })
        
        return imports
    
    def _collect_python_used_names(self, tree: ast.AST) -> Set[str]:
        """收集Python文件中使用的所有名称"""
        used_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # 处理属性访问，如 module.function
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
        
        return used_names
    
    def _extract_typescript_import_names(self, import_statement: str) -> List[str]:
        """从TypeScript导入语句中提取导入的名称"""
        names = []
        
        # 处理 import { name1, name2 } from 'module'
        match = re.search(r'import\s+\{([^}]*)\}', import_statement)
        if match:
            imports_str = match.group(1)
            names.extend([name.strip() for name in imports_str.split(',') if name.strip()])
        
        # 处理 import * as name from 'module'
        match = re.search(r'import\s+\*\s+as\s+(\w+)', import_statement)
        if match:
            names.append(match.group(1))
        
        # 处理 import name from 'module'
        match = re.search(r'import\s+(\w+)\s+from', import_statement)
        if match:
            names.append(match.group(1))
        
        return names
    
    def _generate_report(self, result: Dict) -> str:
        """生成清理报告"""
        report = f"""# 🧹 未使用导入清理报告

**清理时间**: {os.popen('date').read().strip()}
**项目路径**: {self.project_root}

## 📊 清理统计总览

- 总清理文件数: {result['total_files_cleaned']}
- 总移除导入数: {result['total_imports_removed']}

### Python文件清理
- 处理文件数: {result['python']['files_processed']}
- 清理文件数: {result['python']['files_cleaned']}
- 移除导入数: {result['python']['imports_removed']}

### TypeScript文件清理
- 处理文件数: {result['typescript']['files_processed']}
- 清理文件数: {result['typescript']['files_cleaned']}
- 移除导入数: {result['typescript']['imports_removed']}

## 🔧 清理的导入类型

### Python导入
1. import module
2. from module import name
3. from module import name1, name2
4. import module as alias

### TypeScript导入
1. import {{ name }} from 'module'
2. import * as name from 'module'
3. import name from 'module'
4. import 'module'

## 📈 预期效果

通过未使用导入清理，预期：
- 减少代码冗余
- 提升编译速度
- 减少打包体积
- 改善代码可读性
- 提升代码质量评分

## 🎯 建议

1. 使用IDE的自动导入功能
2. 定期运行导入清理工具
3. 在代码审查中检查未使用导入
4. 使用ESLint/Pylint规则自动检测
5. 在CI/CD流程中集成导入检查

## ⚠️ 注意事项

1. 某些导入可能用于副作用（如样式文件）
2. 动态导入可能无法被检测到
3. 类型导入在运行时不使用但编译时需要
4. 建议在清理后进行完整测试

"""
        
        return report

def main():
    print("🧹 开始未使用导入清理...")
    
    cleaner = UnusedImportsCleaner('.')
    
    # 执行清理
    result = cleaner.clean_unused_imports()
    
    # 保存报告
    with open('unused_imports_cleanup_report.md', 'w', encoding='utf-8') as f:
        f.write(result['report'])
    
    print(f"✅ 未使用导入清理完成！")
    print(f"📊 总清理文件: {result['total_files_cleaned']}")
    print(f"📊 总移除导入: {result['total_imports_removed']}")
    print(f"📊 Python文件: {result['python']['files_cleaned']} 个文件，{result['python']['imports_removed']} 个导入")
    print(f"📊 TypeScript文件: {result['typescript']['files_cleaned']} 个文件，{result['typescript']['imports_removed']} 个导入")
    print(f"📄 报告已保存到: unused_imports_cleanup_report.md")

if __name__ == '__main__':
    main() 