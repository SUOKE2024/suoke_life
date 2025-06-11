#!/usr/bin/env python3
"""
API文档生成工具
扫描项目中的Python代码，提取docstring并生成API文档
"""

import os
import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import inspect
import re

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIDocGenerator:
    """API文档生成器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.modules: Dict[str, Dict] = {}
        self.classes: Dict[str, Dict] = {}
        self.functions: Dict[str, Dict] = {}
        
        # 忽略的目录和文件
        self.ignore_dirs = {
            '__pycache__', '.git', '.pytest_cache', 'node_modules', 
            '.venv', 'venv', 'env', '.env', 'build', 'dist',
            '.idea', '.vscode', 'logs', 'temp', 'tmp', 'scripts'
        }
        self.ignore_files = {
            'conftest.py', 'setup.py', 'manage.py'
        }
    
    def should_ignore_path(self, path: Path) -> bool:
        """检查是否应该忽略路径"""
        # 检查目录
        for part in path.parts:
            if part in self.ignore_dirs or part.startswith('.'):
                return True
        
        # 检查文件
        if path.name in self.ignore_files:
            return True
        
        # 只处理Python文件
        if path.suffix != '.py':
            return True
        
        return False
    
    def extract_docstring(self, node: ast.AST) -> Optional[str]:
        """提取docstring"""
        if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)) and
            node.body and isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            return node.body[0].value.value
        return None
    
    def extract_function_signature(self, node: ast.FunctionDef) -> str:
        """提取函数签名"""
        args = []
        
        # 处理普通参数
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
        
        # 处理默认参数
        defaults = node.args.defaults
        if defaults:
            for i, default in enumerate(defaults):
                idx = len(args) - len(defaults) + i
                if idx >= 0:
                    args[idx] += f" = {ast.unparse(default)}"
        
        # 处理*args
        if node.args.vararg:
            vararg = f"*{node.args.vararg.arg}"
            if node.args.vararg.annotation:
                vararg += f": {ast.unparse(node.args.vararg.annotation)}"
            args.append(vararg)
        
        # 处理**kwargs
        if node.args.kwarg:
            kwarg = f"**{node.args.kwarg.arg}"
            if node.args.kwarg.annotation:
                kwarg += f": {ast.unparse(node.args.kwarg.annotation)}"
            args.append(kwarg)
        
        # 处理返回类型
        return_annotation = ""
        if node.returns:
            return_annotation = f" -> {ast.unparse(node.returns)}"
        
        return f"{node.name}({', '.join(args)}){return_annotation}"
    
    def parse_file(self, file_path: Path) -> Dict:
        """解析单个Python文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # 获取模块级docstring
            module_docstring = self.extract_docstring(tree)
            
            module_info = {
                'path': str(file_path),
                'docstring': module_docstring,
                'classes': [],
                'functions': [],
                'imports': []
            }
            
            # 提取导入信息
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_info['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            module_info['imports'].append(f"{node.module}.{alias.name}")
            
            # 提取类和函数信息
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'docstring': self.extract_docstring(node),
                        'methods': [],
                        'line_number': node.lineno
                    }
                    
                    # 提取类方法
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            method_info = {
                                'name': item.name,
                                'signature': self.extract_function_signature(item),
                                'docstring': self.extract_docstring(item),
                                'line_number': item.lineno,
                                'is_async': isinstance(item, ast.AsyncFunctionDef)
                            }
                            class_info['methods'].append(method_info)
                    
                    module_info['classes'].append(class_info)
                
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # 只处理模块级函数，不包括类方法
                    if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) 
                             if hasattr(parent, 'body') and node in getattr(parent, 'body', [])):
                        function_info = {
                            'name': node.name,
                            'signature': self.extract_function_signature(node),
                            'docstring': self.extract_docstring(node),
                            'line_number': node.lineno,
                            'is_async': isinstance(node, ast.AsyncFunctionDef)
                        }
                        module_info['functions'].append(function_info)
            
            return module_info
        
        except Exception as e:
            logger.warning(f"无法解析文件 {file_path}: {e}")
            return None
    
    def scan_project(self):
        """扫描项目中的所有Python文件"""
        logger.info("🔍 扫描项目中的Python文件...")
        
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs and not d.startswith('.')]
            
            for file in files:
                file_path = Path(root) / file
                if not self.should_ignore_path(file_path):
                    python_files.append(file_path)
        
        logger.info(f"找到 {len(python_files)} 个Python文件")
        
        for file_path in python_files:
            module_info = self.parse_file(file_path)
            if module_info:
                # 生成模块名
                relative_path = file_path.relative_to(self.project_root)
                module_name = str(relative_path).replace('/', '.').replace('\\', '.').replace('.py', '')
                self.modules[module_name] = module_info
        
        logger.info(f"解析了 {len(self.modules)} 个模块")
    
    def analyze_documentation_coverage(self) -> Dict:
        """分析文档覆盖率"""
        stats = {
            'total_modules': len(self.modules),
            'documented_modules': 0,
            'total_classes': 0,
            'documented_classes': 0,
            'total_functions': 0,
            'documented_functions': 0,
            'total_methods': 0,
            'documented_methods': 0
        }
        
        for module_name, module_info in self.modules.items():
            if module_info['docstring']:
                stats['documented_modules'] += 1
            
            stats['total_classes'] += len(module_info['classes'])
            stats['total_functions'] += len(module_info['functions'])
            
            for class_info in module_info['classes']:
                if class_info['docstring']:
                    stats['documented_classes'] += 1
                
                stats['total_methods'] += len(class_info['methods'])
                for method_info in class_info['methods']:
                    if method_info['docstring']:
                        stats['documented_methods'] += 1
            
            for function_info in module_info['functions']:
                if function_info['docstring']:
                    stats['documented_functions'] += 1
        
        return stats
    
    def generate_module_doc(self, module_name: str, module_info: Dict) -> str:
        """生成单个模块的文档"""
        doc = f"## {module_name}\n\n"
        
        if module_info['docstring']:
            doc += f"{module_info['docstring']}\n\n"
        else:
            doc += "*无模块文档*\n\n"
        
        doc += f"**文件路径**: `{module_info['path']}`\n\n"
        
        # 导入信息
        if module_info['imports']:
            doc += "### 导入\n\n"
            for imp in sorted(set(module_info['imports'])):
                doc += f"- `{imp}`\n"
            doc += "\n"
        
        # 类文档
        if module_info['classes']:
            doc += "### 类\n\n"
            for class_info in module_info['classes']:
                doc += f"#### {class_info['name']}\n\n"
                if class_info['docstring']:
                    doc += f"{class_info['docstring']}\n\n"
                else:
                    doc += "*无类文档*\n\n"
                
                if class_info['methods']:
                    doc += "**方法**:\n\n"
                    for method_info in class_info['methods']:
                        async_prefix = "async " if method_info['is_async'] else ""
                        doc += f"- `{async_prefix}{method_info['signature']}`"
                        if method_info['docstring']:
                            doc += f": {method_info['docstring'].split('.')[0]}."
                        doc += "\n"
                    doc += "\n"
        
        # 函数文档
        if module_info['functions']:
            doc += "### 函数\n\n"
            for function_info in module_info['functions']:
                async_prefix = "async " if function_info['is_async'] else ""
                doc += f"#### {async_prefix}{function_info['signature']}\n\n"
                if function_info['docstring']:
                    doc += f"{function_info['docstring']}\n\n"
                else:
                    doc += "*无函数文档*\n\n"
        
        return doc
    
    def create_documentation_template(self) -> str:
        """创建文档模板"""
        template = """# API文档模板

## 模块文档规范

### 模块级docstring
```python
\"\"\"
模块简短描述

详细描述模块的功能和用途。

Examples:
    基本用法示例:
    
    >>> from module import function
    >>> result = function()

Note:
    特殊说明或注意事项

Todo:
    * 待完成的功能
    * 需要改进的地方
\"\"\"
```

### 类文档规范
```python
class ExampleClass:
    \"\"\"
    类的简短描述
    
    详细描述类的功能、用途和设计意图。
    
    Attributes:
        attr1 (str): 属性1的描述
        attr2 (int): 属性2的描述
    
    Examples:
        >>> obj = ExampleClass()
        >>> obj.method()
    \"\"\"
```

### 函数文档规范
```python
def example_function(param1: str, param2: int = 0) -> bool:
    \"\"\"
    函数的简短描述
    
    详细描述函数的功能和行为。
    
    Args:
        param1 (str): 参数1的描述
        param2 (int, optional): 参数2的描述. Defaults to 0.
    
    Returns:
        bool: 返回值的描述
    
    Raises:
        ValueError: 什么情况下抛出此异常
        TypeError: 什么情况下抛出此异常
    
    Examples:
        >>> result = example_function("test", 5)
        >>> print(result)
        True
    \"\"\"
```

## 文档编写最佳实践

1. **简洁明了**: 第一行应该是简短的功能描述
2. **详细说明**: 提供足够的细节帮助用户理解
3. **参数说明**: 清楚说明每个参数的类型和用途
4. **返回值**: 说明返回值的类型和含义
5. **异常处理**: 列出可能抛出的异常
6. **示例代码**: 提供实际的使用示例
7. **类型注解**: 使用类型注解提高代码可读性

## 文档生成工具

使用以下命令生成API文档:
```bash
python scripts/generate_api_docs.py
```
"""
        return template
    
    def generate_report(self) -> str:
        """生成API文档报告"""
        logger.info("📊 生成API文档报告...")
        
        stats = self.analyze_documentation_coverage()
        
        # 计算覆盖率
        module_coverage = (stats['documented_modules'] / stats['total_modules'] * 100) if stats['total_modules'] > 0 else 0
        class_coverage = (stats['documented_classes'] / stats['total_classes'] * 100) if stats['total_classes'] > 0 else 0
        function_coverage = (stats['documented_functions'] / stats['total_functions'] * 100) if stats['total_functions'] > 0 else 0
        method_coverage = (stats['documented_methods'] / stats['total_methods'] * 100) if stats['total_methods'] > 0 else 0
        
        report = f"""# API文档生成报告

## 📊 文档覆盖率统计

### 总体统计
- **模块总数**: {stats['total_modules']}
- **类总数**: {stats['total_classes']}
- **函数总数**: {stats['total_functions']}
- **方法总数**: {stats['total_methods']}

### 文档覆盖率
- **模块文档覆盖率**: {module_coverage:.1f}% ({stats['documented_modules']}/{stats['total_modules']})
- **类文档覆盖率**: {class_coverage:.1f}% ({stats['documented_classes']}/{stats['total_classes']})
- **函数文档覆盖率**: {function_coverage:.1f}% ({stats['documented_functions']}/{stats['total_functions']})
- **方法文档覆盖率**: {method_coverage:.1f}% ({stats['documented_methods']}/{stats['total_methods']})

## 📚 模块文档

"""
        
        # 按模块名排序
        for module_name in sorted(self.modules.keys()):
            module_info = self.modules[module_name]
            report += self.generate_module_doc(module_name, module_info)
            report += "---\n\n"
        
        report += f"""

## 📋 文档改进建议

### 高优先级
1. **补充模块文档**: {stats['total_modules'] - stats['documented_modules']} 个模块缺少文档
2. **补充类文档**: {stats['total_classes'] - stats['documented_classes']} 个类缺少文档
3. **补充函数文档**: {stats['total_functions'] - stats['documented_functions']} 个函数缺少文档

### 中优先级
1. **完善方法文档**: {stats['total_methods'] - stats['documented_methods']} 个方法缺少文档
2. **添加类型注解**: 提高代码可读性和IDE支持
3. **添加使用示例**: 在文档中提供实际的使用示例

### 低优先级
1. **统一文档风格**: 确保所有文档遵循相同的格式
2. **添加更多细节**: 为复杂的函数和类添加更详细的说明
3. **生成在线文档**: 使用Sphinx等工具生成在线API文档

## 🛠️ 下一步行动

1. 查看文档模板: `docs/development/documentation_template.md`
2. 按优先级补充缺失的文档
3. 建立文档审查机制
4. 定期运行此工具检查文档覆盖率

---
*报告生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report

def main():
    """主函数"""
    project_root = os.getcwd()
    print('📚 索克生活项目 - API文档生成工具')
    print('=' * 60)
    
    generator = APIDocGenerator(project_root)
    
    # 1. 扫描项目
    generator.scan_project()
    
    # 2. 创建文档模板
    print("📝 创建文档模板...")
    template_content = generator.create_documentation_template()
    
    # 确保目录存在
    docs_dir = Path(project_root) / 'docs' / 'development'
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    template_file = docs_dir / 'documentation_template.md'
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✅ 已创建文档模板: {template_file}")
    
    # 3. 生成报告
    print("📊 生成报告...")
    report = generator.generate_report()
    
    # 保存报告
    report_file = Path(project_root) / 'api_documentation_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📊 API文档报告已保存到: {report_file}")
    
    # 统计信息
    stats = generator.analyze_documentation_coverage()
    total_items = stats['total_modules'] + stats['total_classes'] + stats['total_functions'] + stats['total_methods']
    documented_items = stats['documented_modules'] + stats['documented_classes'] + stats['documented_functions'] + stats['documented_methods']
    
    if total_items > 0:
        overall_coverage = documented_items / total_items * 100
        print(f"\n📈 总体文档覆盖率: {overall_coverage:.1f}% ({documented_items}/{total_items})")
    else:
        print("\n✅ 项目结构分析完成")

if __name__ == "__main__":
    main()
