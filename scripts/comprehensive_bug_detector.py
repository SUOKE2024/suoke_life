#!/usr/bin/env python3
"""
索克生活项目综合Bug检测器
系统性检查和识别项目中的各种Bug
"""

import os
import ast
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import time
from collections import defaultdict

class ComprehensiveBugDetector:
    """综合Bug检测器"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.bug_report = {
            "syntax_errors": [],
            "import_errors": [],
            "type_errors": [],
            "runtime_errors": [],
            "configuration_errors": [],
            "dependency_errors": [],
            "logic_errors": [],
            "performance_issues": []
        }
        
    def detect_all_bugs(self) -> Dict[str, Any]:
        """检测所有类型的Bug"""
        print("🔍 开始综合Bug检测...")
        print("🎯 系统性检查项目中的各种Bug")
        print("=" * 60)
        
        start_time = time.time()
        
        # 1. 语法错误检测
        self._detect_syntax_errors()
        
        # 2. 导入错误检测
        self._detect_import_errors()
        
        # 3. 类型错误检测
        self._detect_type_errors()
        
        # 4. 配置错误检测
        self._detect_configuration_errors()
        
        # 5. 依赖错误检测
        self._detect_dependency_errors()
        
        # 6. 运行时错误检测
        self._detect_runtime_errors()
        
        # 7. 逻辑错误检测
        self._detect_logic_errors()
        
        # 8. 性能问题检测
        self._detect_performance_issues()
        
        end_time = time.time()
        detection_time = end_time - start_time
        
        # 生成Bug报告
        bug_summary = self._generate_bug_report(detection_time)
        
        return bug_summary
    
    def _detect_syntax_errors(self) -> None:
        """检测语法错误"""
        print("🔍 检测语法错误...")
        
        python_files = list(self.project_root.rglob("*.py"))
        typescript_files = list(self.project_root.rglob("*.ts*"))
        
        # 检查Python语法错误
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    self.bug_report["syntax_errors"].append({
                        "file": str(py_file),
                        "line": e.lineno,
                        "column": e.offset,
                        "message": str(e.msg),
                        "type": "Python语法错误",
                        "severity": "HIGH"
                    })
                except Exception as e:
                    self.bug_report["syntax_errors"].append({
                        "file": str(py_file),
                        "line": 0,
                        "column": 0,
                        "message": str(e),
                        "type": "Python解析错误",
                        "severity": "MEDIUM"
                    })
                    
            except UnicodeDecodeError:
                self.bug_report["syntax_errors"].append({
                    "file": str(py_file),
                    "line": 0,
                    "column": 0,
                    "message": "文件编码错误",
                    "type": "编码错误",
                    "severity": "MEDIUM"
                })
        
        # 检查TypeScript语法错误（简化版）
        for ts_file in typescript_files:
            if self._should_skip_file(ts_file):
                continue
                
            try:
                with open(ts_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查常见的TypeScript语法问题
                self._check_typescript_syntax(ts_file, content)
                
            except UnicodeDecodeError:
                self.bug_report["syntax_errors"].append({
                    "file": str(ts_file),
                    "line": 0,
                    "column": 0,
                    "message": "文件编码错误",
                    "type": "编码错误",
                    "severity": "MEDIUM"
                })
        
        print(f"  发现语法错误: {len(self.bug_report['syntax_errors'])}个")
    
    def _check_typescript_syntax(self, file_path: Path, content: str) -> None:
        """检查TypeScript语法问题"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查未闭合的括号
            if line.count('(') != line.count(')'):
                self.bug_report["syntax_errors"].append({
                    "file": str(file_path),
                    "line": i,
                    "column": 0,
                    "message": "括号不匹配",
                    "type": "TypeScript语法错误",
                    "severity": "HIGH"
                })
            
            # 检查未闭合的大括号
            if line.count('{') != line.count('}'):
                self.bug_report["syntax_errors"].append({
                    "file": str(file_path),
                    "line": i,
                    "column": 0,
                    "message": "大括号不匹配",
                    "type": "TypeScript语法错误",
                    "severity": "HIGH"
                })
            
            # 检查重复的分号
            if ';;' in line:
                self.bug_report["syntax_errors"].append({
                    "file": str(file_path),
                    "line": i,
                    "column": line.find(';;'),
                    "message": "重复的分号",
                    "type": "TypeScript语法错误",
                    "severity": "LOW"
                })
    
    def _detect_import_errors(self) -> None:
        """检测导入错误"""
        print("🔍 检测导入错误...")
        
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查导入问题
                self._check_python_imports(py_file, content)
                
            except Exception:
                continue
        
        print(f"  发现导入错误: {len(self.bug_report['import_errors'])}个")
    
    def _check_python_imports(self, file_path: Path, content: str) -> None:
        """检查Python导入问题"""
        lines = content.split('\n')
        
        import_section_ended = False
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            if line.startswith(('import ', 'from ')):
                if import_section_ended:
                    self.bug_report["import_errors"].append({
                        "file": str(file_path),
                        "line": i,
                        "message": "导入语句不在文件顶部",
                        "type": "导入顺序错误",
                        "severity": "LOW"
                    })
                
                # 检查循环导入
                if 'from .' in line and file_path.name in line:
                    self.bug_report["import_errors"].append({
                        "file": str(file_path),
                        "line": i,
                        "message": "可能的循环导入",
                        "type": "循环导入",
                        "severity": "HIGH"
                    })
                
                # 检查未使用的导入
                imported_items = self._extract_imported_items(line)
                if imported_items and not self._check_import_usage(content, imported_items):
                    self.bug_report["import_errors"].append({
                        "file": str(file_path),
                        "line": i,
                        "message": f"未使用的导入: {', '.join(imported_items)}",
                        "type": "未使用导入",
                        "severity": "LOW"
                    })
            else:
                import_section_ended = True
    
    def _extract_imported_items(self, import_line: str) -> List[str]:
        """提取导入的项目"""
        items = []
        
        if import_line.startswith('import '):
            # import module
            module = import_line[7:].split(' as ')[0].strip()
            items.append(module.split('.')[0])
        elif import_line.startswith('from '):
            # from module import items
            parts = import_line.split(' import ')
            if len(parts) == 2:
                import_items = parts[1].split(',')
                for item in import_items:
                    item = item.split(' as ')[0].strip()
                    if item != '*':
                        items.append(item)
        
        return items
    
    def _check_import_usage(self, content: str, imported_items: List[str]) -> bool:
        """检查导入项是否被使用"""
        for item in imported_items:
            if item in content:
                return True
        return False
    
    def _detect_type_errors(self) -> None:
        """检测类型错误"""
        print("🔍 检测类型错误...")
        
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查类型注解问题
                self._check_type_annotations(py_file, content)
                
            except Exception:
                continue
        
        print(f"  发现类型错误: {len(self.bug_report['type_errors'])}个")
    
    def _check_type_annotations(self, file_path: Path, content: str) -> None:
        """检查类型注解问题"""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 检查函数缺少返回类型注解
                    if node.returns is None and node.name != '__init__':
                        self.bug_report["type_errors"].append({
                            "file": str(file_path),
                            "line": node.lineno,
                            "message": f"函数 '{node.name}' 缺少返回类型注解",
                            "type": "缺少类型注解",
                            "severity": "MEDIUM"
                        })
                    
                    # 检查参数缺少类型注解
                    for arg in node.args.args:
                        if arg.annotation is None and arg.arg != 'self':
                            self.bug_report["type_errors"].append({
                                "file": str(file_path),
                                "line": node.lineno,
                                "message": f"参数 '{arg.arg}' 缺少类型注解",
                                "type": "缺少类型注解",
                                "severity": "LOW"
                            })
                
                elif isinstance(node, ast.AnnAssign):
                    # 检查类型注解语法
                    if node.annotation is None:
                        self.bug_report["type_errors"].append({
                            "file": str(file_path),
                            "line": node.lineno,
                            "message": "变量声明缺少类型注解",
                            "type": "缺少类型注解",
                            "severity": "LOW"
                        })
        
        except SyntaxError:
            # 语法错误已在语法检查中处理
            pass
    
    def _detect_configuration_errors(self) -> None:
        """检测配置错误"""
        print("🔍 检测配置错误...")
        
        # 检查package.json
        self._check_package_json()
        
        # 检查tsconfig.json
        self._check_tsconfig()
        
        # 检查React Native配置
        self._check_react_native_config()
        
        # 检查Python配置
        self._check_python_config()
        
        print(f"  发现配置错误: {len(self.bug_report['configuration_errors'])}个")
    
    def _check_package_json(self) -> None:
        """检查package.json配置"""
        package_json_path = self.project_root / "package.json"
        
        if not package_json_path.exists():
            self.bug_report["configuration_errors"].append({
                "file": "package.json",
                "message": "缺少package.json文件",
                "type": "配置文件缺失",
                "severity": "HIGH"
            })
            return
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            # 检查必要字段
            required_fields = ["name", "version", "scripts"]
            for field in required_fields:
                if field not in package_data:
                    self.bug_report["configuration_errors"].append({
                        "file": "package.json",
                        "message": f"缺少必要字段: {field}",
                        "type": "配置字段缺失",
                        "severity": "MEDIUM"
                    })
            
            # 检查脚本配置
            if "scripts" in package_data:
                scripts = package_data["scripts"]
                if "start" not in scripts:
                    self.bug_report["configuration_errors"].append({
                        "file": "package.json",
                        "message": "缺少start脚本",
                        "type": "脚本配置缺失",
                        "severity": "MEDIUM"
                    })
        
        except json.JSONDecodeError as e:
            self.bug_report["configuration_errors"].append({
                "file": "package.json",
                "message": f"JSON格式错误: {str(e)}",
                "type": "JSON格式错误",
                "severity": "HIGH"
            })
    
    def _check_tsconfig(self) -> None:
        """检查TypeScript配置"""
        tsconfig_path = self.project_root / "tsconfig.json"
        
        if not tsconfig_path.exists():
            self.bug_report["configuration_errors"].append({
                "file": "tsconfig.json",
                "message": "缺少tsconfig.json文件",
                "type": "配置文件缺失",
                "severity": "MEDIUM"
            })
            return
        
        try:
            with open(tsconfig_path, 'r', encoding='utf-8') as f:
                tsconfig_data = json.load(f)
            
            # 检查编译选项
            if "compilerOptions" not in tsconfig_data:
                self.bug_report["configuration_errors"].append({
                    "file": "tsconfig.json",
                    "message": "缺少compilerOptions配置",
                    "type": "配置字段缺失",
                    "severity": "HIGH"
                })
        
        except json.JSONDecodeError as e:
            self.bug_report["configuration_errors"].append({
                "file": "tsconfig.json",
                "message": f"JSON格式错误: {str(e)}",
                "type": "JSON格式错误",
                "severity": "HIGH"
            })
    
    def _check_react_native_config(self) -> None:
        """检查React Native配置"""
        # 检查react-native.config.js
        rn_config_path = self.project_root / "react-native.config.js"
        
        if rn_config_path.exists():
            try:
                with open(rn_config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查配置语法
                if 'module.exports' not in content:
                    self.bug_report["configuration_errors"].append({
                        "file": "react-native.config.js",
                        "message": "缺少module.exports导出",
                        "type": "配置语法错误",
                        "severity": "MEDIUM"
                    })
            
            except Exception as e:
                self.bug_report["configuration_errors"].append({
                    "file": "react-native.config.js",
                    "message": f"配置文件读取错误: {str(e)}",
                    "type": "配置文件错误",
                    "severity": "MEDIUM"
                })
    
    def _check_python_config(self) -> None:
        """检查Python配置"""
        # 检查requirements.txt
        requirements_path = self.project_root / "requirements.txt"
        
        if requirements_path.exists():
            try:
                with open(requirements_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 检查版本固定
                        if '==' not in line and '>=' not in line and '~=' not in line:
                            self.bug_report["configuration_errors"].append({
                                "file": "requirements.txt",
                                "line": i,
                                "message": f"依赖 '{line}' 没有指定版本",
                                "type": "依赖版本未固定",
                                "severity": "LOW"
                            })
            
            except Exception as e:
                self.bug_report["configuration_errors"].append({
                    "file": "requirements.txt",
                    "message": f"依赖文件读取错误: {str(e)}",
                    "type": "配置文件错误",
                    "severity": "MEDIUM"
                })
    
    def _detect_dependency_errors(self) -> None:
        """检测依赖错误"""
        print("🔍 检测依赖错误...")
        
        # 检查Node.js依赖
        self._check_node_dependencies()
        
        # 检查Python依赖
        self._check_python_dependencies()
        
        print(f"  发现依赖错误: {len(self.bug_report['dependency_errors'])}个")
    
    def _check_node_dependencies(self) -> None:
        """检查Node.js依赖"""
        package_json_path = self.project_root / "package.json"
        node_modules_path = self.project_root / "node_modules"
        
        if not package_json_path.exists():
            return
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            dependencies = package_data.get("dependencies", {})
            dev_dependencies = package_data.get("devDependencies", {})
            
            all_deps = {**dependencies, **dev_dependencies}
            
            # 检查node_modules是否存在
            if not node_modules_path.exists():
                self.bug_report["dependency_errors"].append({
                    "file": "package.json",
                    "message": "node_modules目录不存在，需要运行npm install",
                    "type": "依赖未安装",
                    "severity": "HIGH"
                })
            else:
                # 检查关键依赖是否安装
                for dep_name in all_deps:
                    dep_path = node_modules_path / dep_name
                    if not dep_path.exists():
                        self.bug_report["dependency_errors"].append({
                            "file": "package.json",
                            "message": f"依赖 '{dep_name}' 未安装",
                            "type": "依赖缺失",
                            "severity": "MEDIUM"
                        })
        
        except Exception:
            pass
    
    def _check_python_dependencies(self) -> None:
        """检查Python依赖"""
        requirements_path = self.project_root / "requirements.txt"
        
        if not requirements_path.exists():
            return
        
        try:
            # 获取已安装的包
            result = subprocess.run(
                ["pip", "list", "--format=freeze"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                installed_packages = set()
                for line in result.stdout.split('\n'):
                    if '==' in line:
                        package_name = line.split('==')[0].lower()
                        installed_packages.add(package_name)
                
                # 检查requirements.txt中的包是否已安装
                with open(requirements_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            package_name = line.split('==')[0].split('>=')[0].split('~=')[0].lower()
                            if package_name not in installed_packages:
                                self.bug_report["dependency_errors"].append({
                                    "file": "requirements.txt",
                                    "line": line_num,
                                    "message": f"Python包 '{package_name}' 未安装",
                                    "type": "Python依赖缺失",
                                    "severity": "MEDIUM"
                                })
        
        except Exception:
            pass
    
    def _detect_runtime_errors(self) -> None:
        """检测运行时错误"""
        print("🔍 检测运行时错误...")
        
        # 检查常见的运行时错误模式
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self._check_runtime_patterns(py_file, content)
                
            except Exception:
                continue
        
        print(f"  发现运行时错误: {len(self.bug_report['runtime_errors'])}个")
    
    def _check_runtime_patterns(self, file_path: Path, content: str) -> None:
        """检查运行时错误模式"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 检查除零错误
            if '/ 0' in line or '// 0' in line:
                self.bug_report["runtime_errors"].append({
                    "file": str(file_path),
                    "line": i,
                    "message": "可能的除零错误",
                    "type": "除零错误",
                    "severity": "HIGH"
                })
            
            # 检查空指针访问
            if '.get(' not in line and '[' in line and ']' in line:
                if 'None[' in line or 'null[' in line:
                    self.bug_report["runtime_errors"].append({
                        "file": str(file_path),
                        "line": i,
                        "message": "可能的空指针访问",
                        "type": "空指针访问",
                        "severity": "HIGH"
                    })
            
            # 检查未处理的异常
            if 'raise ' in line and 'try:' not in content:
                self.bug_report["runtime_errors"].append({
                    "file": str(file_path),
                    "line": i,
                    "message": "抛出异常但可能未被捕获",
                    "type": "未处理异常",
                    "severity": "MEDIUM"
                })
    
    def _detect_logic_errors(self) -> None:
        """检测逻辑错误"""
        print("🔍 检测逻辑错误...")
        
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self._check_logic_patterns(py_file, content)
                
            except Exception:
                continue
        
        print(f"  发现逻辑错误: {len(self.bug_report['logic_errors'])}个")
    
    def _check_logic_patterns(self, file_path: Path, content: str) -> None:
        """检查逻辑错误模式"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 检查重复的条件
            if 'if ' in line and 'and ' in line:
                conditions = line.split(' and ')
                if len(conditions) != len(set(conditions)):
                    self.bug_report["logic_errors"].append({
                        "file": str(file_path),
                        "line": i,
                        "message": "重复的条件判断",
                        "type": "重复条件",
                        "severity": "LOW"
                    })
            
            # 检查永远为真的条件
            if 'if True:' in line or 'while True:' in line:
                if 'break' not in content[content.find(line):]:
                    self.bug_report["logic_errors"].append({
                        "file": str(file_path),
                        "line": i,
                        "message": "可能的无限循环",
                        "type": "无限循环",
                        "severity": "HIGH"
                    })
            
            # 检查空的异常处理
            if 'except:' in line or 'except Exception:' in line:
                next_lines = lines[i:i+3] if i < len(lines) - 2 else lines[i:]
                if all(not l.strip() or l.strip() == 'pass' for l in next_lines):
                    self.bug_report["logic_errors"].append({
                        "file": str(file_path),
                        "line": i,
                        "message": "空的异常处理",
                        "type": "空异常处理",
                        "severity": "MEDIUM"
                    })
    
    def _detect_performance_issues(self) -> None:
        """检测性能问题"""
        print("🔍 检测性能问题...")
        
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self._check_performance_patterns(py_file, content)
                
            except Exception:
                continue
        
        print(f"  发现性能问题: {len(self.bug_report['performance_issues'])}个")
    
    def _check_performance_patterns(self, file_path: Path, content: str) -> None:
        """检查性能问题模式"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 检查低效的字符串拼接
            if '+=' in line and 'str' in line:
                self.bug_report["performance_issues"].append({
                    "file": str(file_path),
                    "line": i,
                    "message": "低效的字符串拼接，建议使用join()",
                    "type": "字符串拼接性能",
                    "severity": "LOW"
                })
            
            # 检查嵌套循环
            if 'for ' in line and i < len(lines) - 1:
                next_line = lines[i].strip()
                if 'for ' in next_line:
                    self.bug_report["performance_issues"].append({
                        "file": str(file_path),
                        "line": i,
                        "message": "嵌套循环可能影响性能",
                        "type": "嵌套循环",
                        "severity": "MEDIUM"
                    })
            
            # 检查重复的数据库查询
            if any(keyword in line.lower() for keyword in ['select', 'query', 'find']):
                if 'for ' in lines[max(0, i-3):i]:
                    self.bug_report["performance_issues"].append({
                        "file": str(file_path),
                        "line": i,
                        "message": "循环中的数据库查询可能影响性能",
                        "type": "循环查询",
                        "severity": "HIGH"
                    })
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = [
            '__pycache__', '.venv', 'venv', '.git', 'node_modules',
            '.pytest_cache', 'htmlcov', '.ruff_cache', '.coverage',
            'coverage.xml', '.benchmarks', 'Pods', '.xcodeproj',
            'android/app/build', 'ios/build'
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _generate_bug_report(self, detection_time: float) -> Dict[str, Any]:
        """生成Bug报告"""
        print("\n" + "=" * 60)
        print("📋 生成Bug检测报告...")
        
        # 统计Bug数量
        total_bugs = sum(len(bugs) for bugs in self.bug_report.values())
        
        # 按严重程度分类
        severity_count = defaultdict(int)
        for bug_type, bugs in self.bug_report.items():
            for bug in bugs:
                severity_count[bug.get('severity', 'UNKNOWN')] += 1
        
        # 按类型分类
        type_count = {bug_type: len(bugs) for bug_type, bugs in self.bug_report.items()}
        
        report_summary = {
            "detection_time": f"{detection_time:.2f}秒",
            "total_bugs": total_bugs,
            "severity_breakdown": dict(severity_count),
            "type_breakdown": type_count,
            "detailed_bugs": self.bug_report
        }
        
        # 保存详细报告
        self._save_bug_report(report_summary)
        
        return report_summary
    
    def _save_bug_report(self, report: Dict[str, Any]) -> None:
        """保存Bug报告"""
        report_path = "BUG_DETECTION_REPORT.md"
        
        content = f"""# 索克生活项目Bug检测报告

## 🔍 检测概览

**检测时间**: {time.strftime("%Y-%m-%d %H:%M:%S")}  
**检测耗时**: {report['detection_time']}  
**发现Bug总数**: {report['total_bugs']}个  

---

## 📊 Bug统计

### 按严重程度分类

| 严重程度 | 数量 | 占比 |
|----------|------|------|
| **HIGH** | {report['severity_breakdown'].get('HIGH', 0)} | {report['severity_breakdown'].get('HIGH', 0) / max(report['total_bugs'], 1) * 100:.1f}% |
| **MEDIUM** | {report['severity_breakdown'].get('MEDIUM', 0)} | {report['severity_breakdown'].get('MEDIUM', 0) / max(report['total_bugs'], 1) * 100:.1f}% |
| **LOW** | {report['severity_breakdown'].get('LOW', 0)} | {report['severity_breakdown'].get('LOW', 0) / max(report['total_bugs'], 1) * 100:.1f}% |

### 按类型分类

| Bug类型 | 数量 | 状态 |
|---------|------|------|
| **语法错误** | {report['type_breakdown']['syntax_errors']} | {'🔴 需要修复' if report['type_breakdown']['syntax_errors'] > 0 else '✅ 正常'} |
| **导入错误** | {report['type_breakdown']['import_errors']} | {'🔴 需要修复' if report['type_breakdown']['import_errors'] > 0 else '✅ 正常'} |
| **类型错误** | {report['type_breakdown']['type_errors']} | {'🔴 需要修复' if report['type_breakdown']['type_errors'] > 0 else '✅ 正常'} |
| **配置错误** | {report['type_breakdown']['configuration_errors']} | {'🔴 需要修复' if report['type_breakdown']['configuration_errors'] > 0 else '✅ 正常'} |
| **依赖错误** | {report['type_breakdown']['dependency_errors']} | {'🔴 需要修复' if report['type_breakdown']['dependency_errors'] > 0 else '✅ 正常'} |
| **运行时错误** | {report['type_breakdown']['runtime_errors']} | {'🔴 需要修复' if report['type_breakdown']['runtime_errors'] > 0 else '✅ 正常'} |
| **逻辑错误** | {report['type_breakdown']['logic_errors']} | {'🔴 需要修复' if report['type_breakdown']['logic_errors'] > 0 else '✅ 正常'} |
| **性能问题** | {report['type_breakdown']['performance_issues']} | {'🔴 需要修复' if report['type_breakdown']['performance_issues'] > 0 else '✅ 正常'} |

---

## 🔍 详细Bug列表

"""
        
        # 添加详细Bug信息
        for bug_type, bugs in report['detailed_bugs'].items():
            if bugs:
                content += f"### {bug_type.replace('_', ' ').title()} ({len(bugs)}个)\n\n"
                
                for i, bug in enumerate(bugs[:10], 1):  # 只显示前10个
                    content += f"**{i}. {bug.get('type', 'Unknown')}** - {bug.get('severity', 'UNKNOWN')}\n"
                    content += f"- **文件**: `{bug.get('file', 'Unknown')}`\n"
                    if 'line' in bug:
                        content += f"- **行号**: {bug['line']}\n"
                    content += f"- **描述**: {bug.get('message', 'No description')}\n\n"
                
                if len(bugs) > 10:
                    content += f"... 还有 {len(bugs) - 10} 个类似问题\n\n"
        
        content += f"""---

## 🎯 修复建议

### 高优先级修复 (HIGH)
{self._generate_fix_suggestions('HIGH', report)}

### 中优先级修复 (MEDIUM)
{self._generate_fix_suggestions('MEDIUM', report)}

### 低优先级修复 (LOW)
{self._generate_fix_suggestions('LOW', report)}

---

## 📈 质量改进计划

### 短期目标 (1-2周)
1. **修复所有HIGH级别Bug**
2. **解决关键配置问题**
3. **修复语法错误**
4. **解决依赖问题**

### 中期目标 (1-2月)
1. **修复所有MEDIUM级别Bug**
2. **优化代码结构**
3. **完善类型注解**
4. **提升代码质量**

### 长期目标 (3-6月)
1. **修复所有LOW级别Bug**
2. **性能优化**
3. **建立质量监控**
4. **持续改进流程**

---

**🔍 Bug检测完成时间**: {time.strftime("%Y-%m-%d %H:%M:%S")}  
**检测工具**: 索克生活综合Bug检测器  
**检测状态**: {'🔴 发现问题' if report['total_bugs'] > 0 else '✅ 质量良好'} 🔍
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📋 Bug检测报告已保存到: {report_path}")
    
    def _generate_fix_suggestions(self, severity: str, report: Dict[str, Any]) -> str:
        """生成修复建议"""
        suggestions = []
        
        for bug_type, bugs in report['detailed_bugs'].items():
            high_bugs = [bug for bug in bugs if bug.get('severity') == severity]
            if high_bugs:
                if bug_type == 'syntax_errors':
                    suggestions.append("- 使用IDE或linter检查语法错误")
                elif bug_type == 'import_errors':
                    suggestions.append("- 整理导入语句，移除未使用的导入")
                elif bug_type == 'type_errors':
                    suggestions.append("- 添加类型注解，提升代码类型安全")
                elif bug_type == 'configuration_errors':
                    suggestions.append("- 检查和修复配置文件")
                elif bug_type == 'dependency_errors':
                    suggestions.append("- 安装缺失的依赖包")
                elif bug_type == 'runtime_errors':
                    suggestions.append("- 添加异常处理和边界检查")
                elif bug_type == 'logic_errors':
                    suggestions.append("- 重构逻辑，消除重复和错误")
                elif bug_type == 'performance_issues':
                    suggestions.append("- 优化算法和数据结构")
        
        return '\n'.join(suggestions) if suggestions else "- 暂无此级别的问题需要修复"

def main():
    """主函数"""
    detector = ComprehensiveBugDetector()
    
    print("🔍 启动综合Bug检测器...")
    print("🎯 系统性检查项目中的各种Bug")
    
    # 执行Bug检测
    results = detector.detect_all_bugs()
    
    print("\n" + "🔍" * 20)
    print("🏆 Bug检测完成！")
    print(f"📊 发现Bug总数: {results['total_bugs']}个")
    print(f"⚠️ 高危Bug: {results['severity_breakdown'].get('HIGH', 0)}个")
    print(f"⚠️ 中危Bug: {results['severity_breakdown'].get('MEDIUM', 0)}个")
    print(f"⚠️ 低危Bug: {results['severity_breakdown'].get('LOW', 0)}个")
    print("🔍" * 20)

if __name__ == "__main__":
    main() 