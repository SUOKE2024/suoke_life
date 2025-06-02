#!/usr/bin/env python3
"""
索克生活项目 GIL 优化建议生成器
分析项目代码并生成具体的优化建议
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class GILIssue:
    """GIL问题描述"""
    file_path: str
    line_number: int
    issue_type: str
    severity: str  # high, medium, low
    description: str
    current_code: str
    suggested_fix: str
    performance_impact: str


class GILOptimizationAnalyzer:
    """GIL优化分析器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues: List[GILIssue] = []
        
        # 定义问题模式
        self.patterns = {
            'thread_pool_executor': {
                'pattern': r'ThreadPoolExecutor\s*\(',
                'severity': 'high',
                'description': 'ThreadPoolExecutor用于CPU密集型任务，受GIL限制'
            },
            'threading_lock': {
                'pattern': r'threading\.Lock\(\)|from\s+threading\s+import.*Lock',
                'severity': 'medium',
                'description': '显式线程锁可能导致GIL竞争'
            }
        }
    
    def analyze_file(self, file_path: Path) -> List[GILIssue]:
        """分析单个文件"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            print(f"无法读取文件 {file_path}: {e}")
            return issues
        
        # 检查每个模式
        for pattern_name, pattern_info in self.patterns.items():
            matches = re.finditer(pattern_info['pattern'], content, re.MULTILINE | re.IGNORECASE)
            
            for match in matches:
                # 找到匹配的行号
                line_number = content[:match.start()].count('\n') + 1
                current_line = lines[line_number - 1] if line_number <= len(lines) else ""
                
                # 生成优化建议
                suggested_fix = self._generate_fix_suggestion(pattern_name, current_line)
                performance_impact = self._estimate_performance_impact(pattern_name)
                
                issue = GILIssue(
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=line_number,
                    issue_type=pattern_name,
                    severity=pattern_info['severity'],
                    description=pattern_info['description'],
                    current_code=current_line.strip(),
                    suggested_fix=suggested_fix,
                    performance_impact=performance_impact
                )
                
                issues.append(issue)
        
        return issues
    
    def _generate_fix_suggestion(self, pattern_name: str, current_line: str) -> str:
        """生成修复建议"""
        suggestions = {
            'thread_pool_executor': f"""
当前代码（受GIL限制）:
{current_line}

优化建议1: 使用ProcessPoolExecutor
from concurrent.futures import ProcessPoolExecutor
executor = ProcessPoolExecutor(max_workers=4)

优化建议2: 使用异步I/O（如果是I/O密集型）
import asyncio
async def async_task():
    # 异步实现
    pass

优化建议3: 使用Numba JIT（如果是数值计算）
from numba import jit
@jit(nopython=True)
def optimized_computation():
    # JIT编译的计算函数
    pass
""",
            'threading_lock': f"""
当前代码:
{current_line}

优化建议1: 使用asyncio.Lock（异步环境）
import asyncio
lock = asyncio.Lock()

优化建议2: 考虑无锁数据结构
import queue
thread_safe_queue = queue.Queue()

优化建议3: 使用多进程通信
import multiprocessing
manager = multiprocessing.Manager()
shared_dict = manager.dict()
"""
        }
        
        return suggestions.get(pattern_name, f"当前代码: {current_line}\n建议: 考虑使用ProcessPoolExecutor或异步I/O优化")
    
    def _estimate_performance_impact(self, pattern_name: str) -> str:
        """估算性能影响"""
        impacts = {
            'thread_pool_executor': "高影响：可能损失60-80%的多核性能",
            'threading_lock': "中等影响：可能导致线程竞争和上下文切换开销"
        }
        return impacts.get(pattern_name, "影响程度待评估")
    
    def analyze_project(self) -> List[GILIssue]:
        """分析整个项目"""
        print("🔍 开始分析项目GIL问题...")
        
        # 查找所有Python文件
        python_files = list(self.project_root.rglob("*.py"))
        
        # 排除某些目录
        excluded_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', 'venv', '.venv'}
        python_files = [
            f for f in python_files 
            if not any(excluded in f.parts for excluded in excluded_dirs)
        ]
        
        print(f"找到 {len(python_files)} 个Python文件")
        
        all_issues = []
        for file_path in python_files:
            file_issues = self.analyze_file(file_path)
            all_issues.extend(file_issues)
            
            if file_issues:
                print(f"  📄 {file_path.relative_to(self.project_root)}: {len(file_issues)} 个问题")
        
        self.issues = all_issues
        return all_issues
    
    def generate_report(self, output_file: str = "gil_optimization_report.json") -> Dict[str, Any]:
        """生成优化报告"""
        # 按严重程度分组
        high_severity = [issue for issue in self.issues if issue.severity == 'high']
        medium_severity = [issue for issue in self.issues if issue.severity == 'medium']
        low_severity = [issue for issue in self.issues if issue.severity == 'low']
        
        # 按文件分组
        files_with_issues = {}
        for issue in self.issues:
            if issue.file_path not in files_with_issues:
                files_with_issues[issue.file_path] = []
            files_with_issues[issue.file_path].append(issue)
        
        # 生成统计信息
        issue_types = {}
        for issue in self.issues:
            issue_types[issue.issue_type] = issue_types.get(issue.issue_type, 0) + 1
        
        report = {
            'analysis_timestamp': __import__('time').strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_issues': len(self.issues),
                'high_severity': len(high_severity),
                'medium_severity': len(medium_severity),
                'low_severity': len(low_severity),
                'affected_files': len(files_with_issues)
            },
            'issue_types': issue_types,
            'top_affected_files': sorted(
                [(path, len(issues)) for path, issues in files_with_issues.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'high_priority_issues': [
                {
                    'file': issue.file_path,
                    'line': issue.line_number,
                    'type': issue.issue_type,
                    'description': issue.description,
                    'current_code': issue.current_code,
                    'performance_impact': issue.performance_impact
                }
                for issue in high_severity[:20]  # 前20个高优先级问题
            ],
            'optimization_recommendations': self._generate_optimization_plan()
        }
        
        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 优化报告已保存到: {output_file}")
        return report
    
    def _generate_optimization_plan(self) -> Dict[str, Any]:
        """生成优化计划"""
        high_issues = [issue for issue in self.issues if issue.severity == 'high']
        medium_issues = [issue for issue in self.issues if issue.severity == 'medium']
        
        return {
            'phase_1_immediate': {
                'description': '立即优化（1-2周）',
                'targets': [
                    '替换AI推理服务中的ThreadPoolExecutor为ProcessPoolExecutor',
                    '优化缓存管理器使用异步I/O',
                    '修复高优先级GIL瓶颈'
                ],
                'affected_files': len(set(issue.file_path for issue in high_issues)),
                'estimated_performance_gain': '30-50%'
            },
            'phase_2_systematic': {
                'description': '系统优化（1个月）',
                'targets': [
                    '重构数据处理管道使用多进程',
                    '实施Numba JIT编译优化',
                    '完善异步I/O使用'
                ],
                'affected_files': len(set(issue.file_path for issue in medium_issues)),
                'estimated_performance_gain': '50-80%'
            },
            'phase_3_advanced': {
                'description': '高级优化（2-3个月）',
                'targets': [
                    '开发关键算法的C扩展',
                    '微服务架构调整',
                    '性能监控系统完善'
                ],
                'estimated_performance_gain': '80-200%'
            }
        }
    
    def print_summary(self):
        """打印分析摘要"""
        print("\n" + "="*60)
        print("🎯 GIL优化分析摘要")
        print("="*60)
        
        high_count = len([i for i in self.issues if i.severity == 'high'])
        medium_count = len([i for i in self.issues if i.severity == 'medium'])
        low_count = len([i for i in self.issues if i.severity == 'low'])
        
        print(f"总问题数: {len(self.issues)}")
        print(f"🔴 高优先级: {high_count}")
        print(f"🟡 中优先级: {medium_count}")
        print(f"🟢 低优先级: {low_count}")
        
        # 显示最严重的问题
        if high_count > 0:
            print(f"\n⚠️  发现 {high_count} 个高优先级GIL问题，建议立即优化")
            print("\n🔥 最严重的问题:")
            for i, issue in enumerate([i for i in self.issues if i.severity == 'high'][:5], 1):
                print(f"  {i}. {issue.file_path}:{issue.line_number} - {issue.description}")
        
        # 按问题类型统计
        issue_types = {}
        for issue in self.issues:
            issue_types[issue.issue_type] = issue_types.get(issue.issue_type, 0) + 1
        
        if issue_types:
            print(f"\n📊 问题类型分布:")
            for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {issue_type}: {count} 个")


def main():
    """主函数"""
    project_root = os.getcwd()
    analyzer = GILOptimizationAnalyzer(project_root)
    
    # 分析项目
    issues = analyzer.analyze_project()
    
    # 打印摘要
    analyzer.print_summary()
    
    # 生成报告
    report = analyzer.generate_report()
    
    # 显示优化建议
    print(f"\n💡 优化计划:")
    for phase, details in report['optimization_recommendations'].items():
        print(f"\n{details['description']}:")
        for target in details['targets']:
            print(f"  • {target}")
        print(f"  预期性能提升: {details['estimated_performance_gain']}")


if __name__ == "__main__":
    main() 