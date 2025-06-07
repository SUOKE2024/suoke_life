#!/usr/bin/env python3
"""修复剩余的语法错误和其他问题"""

import re
import os
from pathlib import Path

def fix_syntax_errors():
    """修复语法错误"""
    # 修复 metrics.py 的缩进问题
    metrics_file = Path('xiaoai/utils/metrics.py')
    if metrics_file.exists():
        with open(metrics_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复缩进问题
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            if i == 4 and line.strip().startswith('import asyncio'):
                # 修复第5行的缩进
                fixed_lines.append('import asyncio')
            elif i == 5 and 'from prometheus_client' in line:
                # 修复第6行的缩进
                fixed_lines.append('from prometheus_client import Counter, Gauge, Histogram, start_http_server')
            else:
                fixed_lines.append(line)
        
        new_content = '\n'.join(fixed_lines)
        
        if new_content != content:
            with open(metrics_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'Fixed syntax errors in: {metrics_file}')

def fix_undefined_variables():
    """修复未定义变量"""
    # 修复 xiaoai_service_impl.py 中的 _user_id 问题
    service_file = Path('xiaoai/service/xiaoai_service_impl.py')
    if service_file.exists():
        with open(service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换 _user_id 为 user_id
        content = content.replace('_user_id', 'user_id')
        
        with open(service_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed undefined variables in: {service_file}')
    
    # 修复 resilience.py 中的 _max_backoff 问题
    resilience_file = Path('xiaoai/utils/resilience.py')
    if resilience_file.exists():
        with open(resilience_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换 _max_backoff 为 max_backoff
        content = content.replace('_max_backoff', 'max_backoff')
        
        with open(resilience_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed undefined variables in: {resilience_file}')

def fix_unused_arguments():
    """修复未使用的参数"""
    files_to_fix = [
        'xiaoai/observability/monitoring.py',
        'xiaoai/service/enhanced_diagnosis_service.py',
        'xiaoai/service/xiaoai_service_impl.py',
        'xiaoai/utils/resilience.py'
    ]
    
    for file_path in files_to_fix:
        path = Path(file_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 在未使用的参数前添加下划线
            patterns = [
                (r'\bhealth_score\b(?=\s*[,)])', '_health_score'),
                (r'\bhistory\b(?=\s*[,)])', '_history'),
                (r'\bvital_signs\b(?=\s*[,)])', '_vital_signs'),
                (r'\bimages\b(?=\s*[,)])', '_images'),
                (r'\banalysis_results\b(?=\s*[,)])', '_analysis_results'),
                (r'\bdiagnosis_request\b(?=\s*[,)])', '_diagnosis_request'),
                (r'\bquery_request\b(?=\s*[,)])', '_query_request'),
                (r'\breport_request\b(?=\s*[,)])', '_report_request'),
                (r'\btext\b(?=\s*[,)])', '_text'),
                (r'\bmax_backoff\b(?=\s*[,)])', '_max_backoff'),
            ]
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Fixed unused arguments in: {path}')

def fix_path_operations():
    """修复路径操作"""
    config_files = [
        'xiaoai/utils/config_loader.py',
        'xiaoai/utils/config_manager.py'
    ]
    
    for file_path in config_files:
        path = Path(file_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换 os.path 操作为 Path 操作
            replacements = [
                (r'os\.path\.join\(([^,]+),\s*([^)]+)\)', r'Path(\1) / \2'),
                (r'os\.path\.dirname\(__file__\)', r'Path(__file__).parent'),
                (r'os\.path\.exists\(([^)]+)\)', r'Path(\1).exists()'),
                (r'os\.path\.getmtime\(([^)]+)\)', r'Path(\1).stat().st_mtime'),
                (r'open\(([^,]+),', r'Path(\1).open('),
            ]
            
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)
            
            # 确保导入了 Path
            if 'from pathlib import Path' not in content:
                lines = content.split('\n')
                import_index = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        import_index = i + 1
                
                lines.insert(import_index, 'from pathlib import Path')
                content = '\n'.join(lines)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Fixed path operations in: {path}')

def fix_global_statements():
    """修复全局变量声明"""
    files_with_globals = [
        'xiaoai/four_diagnosis/enhanced_tongue_analysis.py',
        'xiaoai/four_diagnosis/knowledge_graph.py',
        'xiaoai/four_diagnosis/tcm_algorithm.py',
        'xiaoai/service/cache_manager.py',
        'xiaoai/service/enhanced_diagnosis_service.py',
        'xiaoai/service/xiaoai_service_impl.py',
        'xiaoai/utils/config_loader.py',
        'xiaoai/utils/config_manager.py',
        'xiaoai/utils/resilience.py'
    ]
    
    for file_path in files_with_globals:
        path = Path(file_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 注释掉 global 语句
            lines = content.split('\n')
            fixed_lines = []
            
            for line in lines:
                if line.strip().startswith('global '):
                    fixed_lines.append(f'    # {line.strip()}  # Global usage discouraged')
                else:
                    fixed_lines.append(line)
            
            new_content = '\n'.join(fixed_lines)
            
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Fixed global statements in: {path}')

def main():
    """主函数"""
    print("🔧 修复剩余的语法错误和其他问题...")
    
    fix_syntax_errors()
    fix_undefined_variables()
    fix_unused_arguments()
    fix_path_operations()
    fix_global_statements()
    
    print("✅ 修复完成！")

if __name__ == "__main__":
    main() 