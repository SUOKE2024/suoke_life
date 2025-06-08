#!/usr/bin/env python3
"""
索克生活项目优先级Bug分析器
专门分析和修复核心服务和智能体服务的语法错误
"""

import os
import ast
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple
import time
import shutil
from collections import defaultdict, Counter

class PriorityBugAnalyzer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.priority_services = {
            'agent_services': [
                'xiaoai-service',
                'xiaoke-service', 
                'laoke-service',
                'soer-service'
            ],
            'core_services': [
                'api-gateway',
                'message-bus',
                'medical-resource-service',
                'health-data-service',
                'auth-service'
            ]
        }
        self.analysis_results = {
            'priority_files': [],
            'critical_errors': [],
            'fixable_errors': [],
            'manual_review_needed': []
        }
        
    def analyze_priority_bugs(self):
        """分析优先级Bug"""
        print('🎯 启动优先级Bug分析...')
        print('🔍 专注核心服务和智能体服务')
        print('=' * 60)
        
        start_time = time.time()
        
        # 1. 识别优先级文件
        self._identify_priority_files()
        
        # 2. 分析关键错误
        self._analyze_critical_errors()
        
        # 3. 分类可修复错误
        self._categorize_fixable_errors()
        
        # 4. 执行优先级修复
        self._execute_priority_fixes()
        
        # 5. 生成分析报告
        end_time = time.time()
        self._generate_priority_report(end_time - start_time)
        
    def _identify_priority_files(self):
        """识别优先级文件"""
        print('📂 识别优先级文件...')
        
        priority_files = []
        
        # 搜索智能体服务文件
        for service in self.priority_services['agent_services']:
            service_path = self.project_root / 'services' / 'agent-services' / service
            if service_path.exists():
                for py_file in service_path.rglob('*.py'):
                    priority_files.append({
                        'path': str(py_file),
                        'category': 'agent_service',
                        'service': service,
                        'priority': 'critical'
                    })
        
        # 搜索核心服务文件
        for service in self.priority_services['core_services']:
            service_path = self.project_root / 'services' / service
            if service_path.exists():
                for py_file in service_path.rglob('*.py'):
                    priority_files.append({
                        'path': str(py_file),
                        'category': 'core_service',
                        'service': service,
                        'priority': 'high'
                    })
        
        # 添加关键目录的主要文件
        key_paths = [
            'src/agents',
            'src/core',
            'src/services'
        ]
        
        for key_path in key_paths:
            path = self.project_root / key_path
            if path.exists():
                for py_file in path.rglob('*.py'):
                    priority_files.append({
                        'path': str(py_file),
                        'category': 'key_file',
                        'service': key_path.split('/')[-1],
                        'priority': 'high'
                    })
        
        self.analysis_results['priority_files'] = priority_files
        print(f'  📊 发现优先级文件: {len(priority_files)}个')
        
    def _analyze_critical_errors(self):
        """分析关键错误"""
        print('🔍 分析关键错误...')
        
        critical_errors = []
        
        for file_info in self.analysis_results['priority_files']:
            file_path = file_info['path']
            
            if not Path(file_path).exists():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 尝试解析语法
                try:
                    ast.parse(content)
                    # 语法正确，跳过
                    continue
                except SyntaxError as e:
                    error_info = {
                        'file': file_path,
                        'category': file_info['category'],
                        'service': file_info['service'],
                        'priority': file_info['priority'],
                        'error': str(e),
                        'line': e.lineno,
                        'text': e.text.strip() if e.text else '',
                        'error_type': self._classify_error(str(e))
                    }
                    critical_errors.append(error_info)
                    
            except Exception as e:
                print(f'  ❌ 无法分析文件 {Path(file_path).name}: {str(e)}')
        
        self.analysis_results['critical_errors'] = critical_errors
        print(f'  📊 发现关键错误: {len(critical_errors)}个')
        
    def _classify_error(self, error_msg: str) -> str:
        """分类错误类型"""
        error_msg = error_msg.lower()
        
        if 'unexpected indent' in error_msg:
            return 'indentation'
        elif 'expected' in error_msg and ':' in error_msg:
            return 'missing_colon'
        elif 'invalid syntax' in error_msg:
            return 'invalid_syntax'
        elif 'was never closed' in error_msg or 'unmatched' in error_msg:
            return 'bracket_mismatch'
        elif 'import' in error_msg:
            return 'import_error'
        else:
            return 'other'
    
    def _categorize_fixable_errors(self):
        """分类可修复错误"""
        print('📋 分类可修复错误...')
        
        fixable_errors = []
        manual_review_needed = []
        
        for error in self.analysis_results['critical_errors']:
            error_type = error['error_type']
            
            # 可自动修复的错误类型
            if error_type in ['indentation', 'missing_colon', 'bracket_mismatch']:
                fixable_errors.append(error)
            else:
                manual_review_needed.append(error)
        
        self.analysis_results['fixable_errors'] = fixable_errors
        self.analysis_results['manual_review_needed'] = manual_review_needed
        
        print(f'  📊 可修复错误: {len(fixable_errors)}个')
        print(f'  📊 需人工审查: {len(manual_review_needed)}个')
        
    def _execute_priority_fixes(self):
        """执行优先级修复"""
        print('🔧 执行优先级修复...')
        
        fixed_count = 0
        total_attempts = 0
        
        # 按优先级排序
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        fixable_errors = sorted(
            self.analysis_results['fixable_errors'],
            key=lambda x: priority_order.get(x['priority'], 3)
        )
        
        for error in fixable_errors:
            file_path = error['file']
            total_attempts += 1
            
            print(f'  🔧 修复文件: {Path(file_path).name} ({error["error_type"]})')
            
            if self._fix_priority_file(file_path, error):
                fixed_count += 1
                print(f'    ✅ 修复成功')
            else:
                print(f'    ❌ 修复失败')
        
        self.analysis_results['fix_stats'] = {
            'total_attempts': total_attempts,
            'successful_fixes': fixed_count,
            'success_rate': (fixed_count / total_attempts * 100) if total_attempts > 0 else 0
        }
        
        print(f'  📊 优先级修复统计: {fixed_count}/{total_attempts} ({fixed_count/total_attempts*100:.1f}%)')
    
    def _fix_priority_file(self, file_path: str, error_info: Dict) -> bool:
        """修复优先级文件"""
        try:
            # 备份原文件
            backup_path = f"{file_path}.backup_priority"
            shutil.copy2(file_path, backup_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            error_type = error_info['error_type']
            
            # 根据错误类型应用特定修复策略
            if error_type == 'indentation':
                fixed_content = self._fix_indentation_error(content, error_info)
            elif error_type == 'missing_colon':
                fixed_content = self._fix_missing_colon_error(content, error_info)
            elif error_type == 'bracket_mismatch':
                fixed_content = self._fix_bracket_error(content, error_info)
            else:
                return False
            
            if fixed_content != original_content:
                # 验证修复后的语法
                try:
                    ast.parse(fixed_content)
                    
                    # 语法正确，保存文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    
                    return True
                    
                except SyntaxError:
                    # 修复失败，恢复原文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                    
                    return False
            
            return False
            
        except Exception as e:
            print(f'    ❌ 修复过程出错: {str(e)}')
            return False
    
    def _fix_indentation_error(self, content: str, error_info: Dict) -> str:
        """修复缩进错误"""
        lines = content.split('\n')
        error_line = error_info.get('line', 1) - 1  # 转换为0索引
        
        if 0 <= error_line < len(lines):
            line = lines[error_line]
            
            # 检查上一行是否以冒号结尾
            if error_line > 0 and lines[error_line - 1].strip().endswith(':'):
                # 添加适当的缩进
                stripped = line.strip()
                if stripped:
                    lines[error_line] = '    ' + stripped
            else:
                # 移除多余的缩进
                lines[error_line] = line.lstrip()
        
        return '\n'.join(lines)
    
    def _fix_missing_colon_error(self, content: str, error_info: Dict) -> str:
        """修复缺少冒号错误"""
        lines = content.split('\n')
        error_line = error_info.get('line', 1) - 1
        
        if 0 <= error_line < len(lines):
            line = lines[error_line].rstrip()
            
            # 检查是否是函数或类定义
            if re.match(r'^\s*(def|class|if|elif|else|for|while|try|except|finally|with)\s', line):
                if not line.endswith(':'):
                    lines[error_line] = line + ':'
        
        return '\n'.join(lines)
    
    def _fix_bracket_error(self, content: str, error_info: Dict) -> str:
        """修复括号错误"""
        lines = content.split('\n')
        error_line = error_info.get('line', 1) - 1
        
        if 0 <= error_line < len(lines):
            line = lines[error_line]
            
            # 简单的括号修复
            open_parens = line.count('(')
            close_parens = line.count(')')
            
            if open_parens > close_parens:
                lines[error_line] = line + ')' * (open_parens - close_parens)
            
            # 修复方括号
            open_brackets = line.count('[')
            close_brackets = line.count(']')
            
            if open_brackets > close_brackets:
                lines[error_line] = lines[error_line] + ']' * (open_brackets - close_brackets)
        
        return '\n'.join(lines)
    
    def _generate_priority_report(self, total_time: float):
        """生成优先级分析报告"""
        print('\n' + '=' * 60)
        print('📋 生成优先级Bug分析报告...')
        
        fix_stats = self.analysis_results.get('fix_stats', {})
        success_rate = fix_stats.get('success_rate', 0)
        
        # 统计错误类型
        error_types = Counter()
        for error in self.analysis_results['critical_errors']:
            error_types[error['error_type']] += 1
        
        # 统计服务分布
        service_errors = Counter()
        for error in self.analysis_results['critical_errors']:
            service_errors[error['service']] += 1
        
        report_content = f"""# 索克生活项目优先级Bug分析报告

## 🎯 优先级分析概览

**分析时间**: {time.strftime("%Y-%m-%d %H:%M:%S")}  
**分析耗时**: {total_time:.2f}秒  
**优先级文件**: {len(self.analysis_results['priority_files'])}个  
**关键错误**: {len(self.analysis_results['critical_errors'])}个  
**修复成功率**: {success_rate:.1f}%  

---

## 📊 关键错误分析

### 错误类型分布

| 错误类型 | 数量 | 占比 | 可修复性 |
|----------|------|------|----------|"""

        total_errors = sum(error_types.values())
        for error_type, count in error_types.most_common():
            percentage = (count / total_errors * 100) if total_errors > 0 else 0
            fixable = '🟢 可修复' if error_type in ['indentation', 'missing_colon', 'bracket_mismatch'] else '🔴 需人工'
            report_content += f"\n| **{error_type}** | {count} | {percentage:.1f}% | {fixable} |"

        report_content += f"""

### 服务错误分布

| 服务名称 | 错误数量 | 优先级 | 状态 |
|----------|----------|--------|------|"""

        for service, count in service_errors.most_common():
            priority = '🔴 关键' if service in self.priority_services['agent_services'] else '🟠 重要'
            status = '🔧 修复中' if count <= 5 else '⚠️ 需关注'
            report_content += f"\n| **{service}** | {count} | {priority} | {status} |"

        report_content += f"""

---

## 🔧 修复执行结果

### 修复统计
- **尝试修复**: {fix_stats.get('total_attempts', 0)}个错误
- **成功修复**: {fix_stats.get('successful_fixes', 0)}个错误
- **修复成功率**: {success_rate:.1f}%
- **剩余错误**: {len(self.analysis_results['manual_review_needed'])}个

---

## 📋 需人工审查的错误

### 高优先级错误"""

        manual_errors = sorted(
            self.analysis_results['manual_review_needed'],
            key=lambda x: {'critical': 0, 'high': 1}.get(x['priority'], 2)
        )

        for i, error in enumerate(manual_errors[:10], 1):
            file_name = Path(error['file']).name
            report_content += f"""

{i}. **{file_name}** ({error['service']})
   - 错误类型: {error['error_type']}
   - 错误信息: {error['error'][:100]}...
   - 优先级: {error['priority']}"""

        if len(manual_errors) > 10:
            report_content += f"\n\n... 还有 {len(manual_errors) - 10} 个错误需要审查"

        report_content += f"""

---

## 🚀 下一步行动计划

### 立即行动 (24小时内)
1. **人工修复关键错误**: 处理{len([e for e in manual_errors if e['priority'] == 'critical'])}个关键错误
2. **验证核心服务**: 确保智能体服务基本可用
3. **运行基础测试**: 验证修复效果

### 短期计划 (1周内)
1. **完善修复工具**: 提升自动修复成功率
2. **建立测试流程**: 确保修复质量
3. **文档更新**: 记录修复过程和经验

---

**🎯 优先级分析完成时间**: {time.strftime("%Y-%m-%d %H:%M:%S")}  
**分析工具**: 索克生活优先级Bug分析器  
**分析状态**: {'🟢 分析成功' if len(self.analysis_results['critical_errors']) > 0 else '🔴 需要进一步分析'} 🎯
"""
        
        # 保存报告
        with open('PRIORITY_BUG_ANALYSIS_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f'📋 优先级Bug分析报告已保存到: PRIORITY_BUG_ANALYSIS_REPORT.md')
        
        # 打印摘要
        print('\n' + '🎯' * 20)
        print('🏆 优先级Bug分析完成！')
        print(f'📂 优先级文件: {len(self.analysis_results["priority_files"])}个')
        print(f'🔍 关键错误: {len(self.analysis_results["critical_errors"])}个')
        print(f'🔧 修复成功率: {success_rate:.1f}%')
        print(f'📋 需人工审查: {len(self.analysis_results["manual_review_needed"])}个')
        print('🎯' * 20)

def main():
    """主函数"""
    analyzer = PriorityBugAnalyzer()
    
    print('🎯 启动优先级Bug分析器...')
    print('🔍 专注核心服务和智能体服务')
    
    # 执行优先级分析
    analyzer.analyze_priority_bugs()

if __name__ == "__main__":
    main() 