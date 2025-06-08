#!/usr/bin/env python3
"""
索克生活项目Bug检测器
"""

import os
import ast
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Any
import time
from collections import defaultdict

class BugDetector:
    def __init__(self):
        self.project_root = Path.cwd()
        self.bug_report = {
            'syntax_errors': [],
            'import_errors': [],
            'configuration_errors': [],
            'dependency_errors': []
        }
        
    def detect_bugs(self):
        print('🔍 开始Bug检测...')
        print('=' * 50)
        
        start_time = time.time()
        
        # 1. 语法错误检测
        self._detect_syntax_errors()
        
        # 2. 导入错误检测
        self._detect_import_errors()
        
        # 3. 配置错误检测
        self._detect_configuration_errors()
        
        # 4. 依赖错误检测
        self._detect_dependency_errors()
        
        end_time = time.time()
        detection_time = end_time - start_time
        
        # 生成报告
        return self._generate_report(detection_time)
    
    def _detect_syntax_errors(self):
        print('🔍 检测语法错误...')
        
        python_files = list(self.project_root.rglob('*.py'))
        syntax_error_count = 0
        
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    self.bug_report['syntax_errors'].append({
                        'file': str(py_file),
                        'line': e.lineno,
                        'message': str(e.msg),
                        'severity': 'HIGH'
                    })
                    syntax_error_count += 1
                    
            except Exception:
                continue
        
        print(f'  发现语法错误: {syntax_error_count}个')
    
    def _detect_import_errors(self):
        print('🔍 检测导入错误...')
        
        python_files = list(self.project_root.rglob('*.py'))
        import_error_count = 0
        
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    line = line.strip()
                    
                    if line.startswith('from .') and py_file.name in line:
                        self.bug_report['import_errors'].append({
                            'file': str(py_file),
                            'line': i,
                            'message': '可能的循环导入',
                            'severity': 'HIGH'
                        })
                        import_error_count += 1
                        
            except Exception:
                continue
        
        print(f'  发现导入错误: {import_error_count}个')
    
    def _detect_configuration_errors(self):
        print('🔍 检测配置错误...')
        
        config_error_count = 0
        
        # 检查package.json
        package_json_path = self.project_root / 'package.json'
        
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                
                # 检查必要字段
                required_fields = ['name', 'version', 'scripts']
                for field in required_fields:
                    if field not in package_data:
                        self.bug_report['configuration_errors'].append({
                            'file': 'package.json',
                            'message': f'缺少必要字段: {field}',
                            'severity': 'MEDIUM'
                        })
                        config_error_count += 1
            
            except json.JSONDecodeError as e:
                self.bug_report['configuration_errors'].append({
                    'file': 'package.json',
                    'message': f'JSON格式错误: {str(e)}',
                    'severity': 'HIGH'
                })
                config_error_count += 1
        
        print(f'  发现配置错误: {config_error_count}个')
    
    def _detect_dependency_errors(self):
        print('🔍 检测依赖错误...')
        
        dependency_error_count = 0
        
        # 检查node_modules
        node_modules_path = self.project_root / 'node_modules'
        
        if not node_modules_path.exists():
            self.bug_report['dependency_errors'].append({
                'file': 'package.json',
                'message': 'node_modules目录不存在，需要运行npm install',
                'severity': 'HIGH'
            })
            dependency_error_count += 1
        
        print(f'  发现依赖错误: {dependency_error_count}个')
    
    def _should_skip_file(self, file_path):
        skip_patterns = [
            '__pycache__', '.venv', 'venv', '.git', 'node_modules',
            '.pytest_cache', 'htmlcov', '.ruff_cache', '.coverage'
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _generate_report(self, detection_time):
        print('\n' + '=' * 50)
        print('📋 生成Bug检测报告...')
        
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
            'detection_time': f'{detection_time:.2f}秒',
            'total_bugs': total_bugs,
            'severity_breakdown': dict(severity_count),
            'type_breakdown': type_count,
            'detailed_bugs': self.bug_report
        }
        
        return report_summary

if __name__ == "__main__":
    detector = BugDetector()
    results = detector.detect_bugs()
    
    print('\n' + '🔍' * 20)
    print('🏆 Bug检测完成！')
    print(f'📊 发现Bug总数: {results["total_bugs"]}个')
    print(f'⚠️ 高危Bug: {results["severity_breakdown"].get("HIGH", 0)}个')
    print(f'⚠️ 中危Bug: {results["severity_breakdown"].get("MEDIUM", 0)}个')
    print(f'⚠️ 低危Bug: {results["severity_breakdown"].get("LOW", 0)}个')
    print('🔍' * 20)
    
    # 保存结果
    with open('bug_detection_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print('📋 Bug检测结果已保存到: bug_detection_results.json') 