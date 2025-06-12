#!/usr/bin/env python3
"""
索克生活项目 - 内存管理优化工具
检测和修复Python代码中的内存管理问题
"""

import ast
import gc
import json
import logging
import os
import re
import subprocess
import sys
import tracemalloc
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class MemoryIssue:
    """内存问题"""

    file_path: str
    line_number: int
    issue_type: str
    description: str
    code_snippet: str
    suggested_fix: str
    severity: str


class MemoryOptimizer:
    """内存管理优化器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues_found = []
        self.backup_dir = self.project_root / "backups" / "memory_optimization"

        # 内存问题检测模式
        self.memory_patterns = {
            "unclosed_file": {
                "patterns": [
                    r"open\s*\([^)]+\)(?!\s*with)",  # open() 不在 with 语句中
                    r"file\s*=\s*open\s*\([^)]+\)",  # file = open() 模式
                ],
                "severity": "HIGH",
                "description": "未正确关闭的文件句柄",
            },
            "large_list_comprehension": {
                "patterns": [
                    r"\[[^\]]{100,}\]",  # 超长列表推导式
                    r"\[[^]]*for[^]]*for[^]]*\]",  # 嵌套列表推导式
                ],
                "severity": "MEDIUM",
                "description": "可能消耗大量内存的列表推导式",
            },
            "global_variables": {
                "patterns": [
                    r"global\s+\w+",
                    r"^\s*[A-Z_][A-Z0-9_]*\s*=.*",  # 全局常量模式
                ],
                "severity": "MEDIUM",
                "description": "全局变量可能导致内存泄漏",
            },
            "circular_reference": {
                "patterns": [r"self\.\w+\s*=\s*self", r"parent\.\w+\s*=\s*child"],
                "severity": "HIGH",
                "description": "可能的循环引用",
            },
            "large_data_structures": {
                "patterns": [
                    r"dict\(\)\s*#.*large",
                    r"list\(\)\s*#.*large",
                    r"\[\]\s*#.*large",
                ],
                "severity": "MEDIUM",
                "description": "大型数据结构",
            },
            "memory_intensive_operations": {
                "patterns": [
                    r"\.read\(\)",  # 读取整个文件
                    r"\.readlines\(\)",  # 读取所有行
                    r"json\.loads\([^)]*\.read\(\)",  # 加载大JSON
                ],
                "severity": "MEDIUM",
                "description": "内存密集型操作",
            },
        }

        # 排除的文件和目录
        self.exclude_patterns = {
            "venv",
            "env",
            ".env",
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            "dist",
            "build",
            ".idea",
            ".vscode",
            "*.pyc",
            "*.pyo",
            "*.egg-info",
        }

    def scan_memory_issues(self) -> List[MemoryIssue]:
        """扫描内存管理问题"""
        logger.info("🔍 扫描内存管理问题...")

        python_files = self._get_python_files()

        for file_path in python_files:
            try:
                self._analyze_file_memory(file_path)
            except Exception as e:
                logger.warning(f"无法分析文件 {file_path}: {e}")

        logger.info(f"发现 {len(self.issues_found)} 个内存问题")
        return self.issues_found

    def _get_python_files(self) -> List[Path]:
        """获取所有Python文件"""
        python_files = []

        for root, dirs, files in os.walk(self.project_root):
            # 排除特定目录
            dirs[:] = [
                d
                for d in dirs
                if not any(pattern in d for pattern in self.exclude_patterns)
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    # 排除备份文件
                    if "backup" not in str(file_path).lower():
                        python_files.append(file_path)

        return python_files

    def _analyze_file_memory(self, file_path: Path):
        """分析单个文件的内存问题"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # 使用AST分析
            try:
                tree = ast.parse(content)
                self._analyze_ast_memory(file_path, tree, lines)
            except SyntaxError:
                # 如果AST解析失败，使用正则表达式
                self._analyze_regex_memory(file_path, lines)

        except Exception as e:
            logger.warning(f"无法读取文件 {file_path}: {e}")

    def _analyze_ast_memory(self, file_path: Path, tree: ast.AST, lines: List[str]):
        """使用AST分析内存问题"""
        for node in ast.walk(tree):
            # 检查文件操作
            if isinstance(node, ast.Call):
                self._check_file_operations(file_path, node, lines)

            # 检查列表推导式
            elif isinstance(node, ast.ListComp):
                self._check_list_comprehension(file_path, node, lines)

            # 检查全局变量
            elif isinstance(node, ast.Global):
                self._check_global_variables(file_path, node, lines)

    def _check_file_operations(self, file_path: Path, node: ast.Call, lines: List[str]):
        """检查文件操作"""
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            line_num = node.lineno
            line_content = lines[line_num - 1] if line_num <= len(lines) else ""

            # 检查是否在with语句中
            if "with" not in line_content:
                issue = MemoryIssue(
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=line_num,
                    issue_type="unclosed_file",
                    description="文件未使用with语句打开，可能导致文件句柄泄漏",
                    code_snippet=line_content.strip(),
                    suggested_fix=self._suggest_file_fix(line_content),
                    severity="HIGH",
                )
                self.issues_found.append(issue)

    def _check_list_comprehension(
        self, file_path: Path, node: ast.ListComp, lines: List[str]
    ):
        """检查列表推导式"""
        line_num = node.lineno
        line_content = lines[line_num - 1] if line_num <= len(lines) else ""

        # 检查嵌套循环
        if len(node.generators) > 1:
            issue = MemoryIssue(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_num,
                issue_type="large_list_comprehension",
                description="嵌套列表推导式可能消耗大量内存",
                code_snippet=line_content.strip(),
                suggested_fix="考虑使用生成器表达式或分步处理",
                severity="MEDIUM",
            )
            self.issues_found.append(issue)

    def _check_global_variables(
        self, file_path: Path, node: ast.Global, lines: List[str]
    ):
        """检查全局变量"""
        line_num = node.lineno
        line_content = lines[line_num - 1] if line_num <= len(lines) else ""

        issue = MemoryIssue(
            file_path=str(file_path.relative_to(self.project_root)),
            line_number=line_num,
            issue_type="global_variables",
            description="全局变量可能导致内存泄漏",
            code_snippet=line_content.strip(),
            suggested_fix="考虑使用类属性或函数参数替代全局变量",
            severity="MEDIUM",
        )
        self.issues_found.append(issue)

    def _analyze_regex_memory(self, file_path: Path, lines: List[str]):
        """使用正则表达式分析内存问题（备用方法）"""
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()

            for pattern_type, pattern_info in self.memory_patterns.items():
                for pattern in pattern_info["patterns"]:
                    if re.search(pattern, line_stripped):
                        issue = MemoryIssue(
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=line_num,
                            issue_type=pattern_type,
                            description=pattern_info["description"],
                            code_snippet=line_stripped,
                            suggested_fix=self._generate_memory_fix(
                                pattern_type, line_stripped
                            ),
                            severity=pattern_info["severity"],
                        )
                        self.issues_found.append(issue)

    def _suggest_file_fix(self, line_content: str) -> str:
        """建议文件操作修复方案"""
        return f"""
建议修复方案：
原代码: {line_content}
修复为:
with open(...) as f:
    # 文件操作
    pass
# 文件会自动关闭
"""

    def _generate_memory_fix(self, issue_type: str, code_snippet: str) -> str:
        """生成内存问题修复建议"""
        fixes = {
            "unclosed_file": "使用 with 语句确保文件正确关闭",
            "large_list_comprehension": "使用生成器表达式: (x for x in ...) 替代 [x for x in ...]",
            "global_variables": "避免使用全局变量，使用类属性或函数参数",
            "circular_reference": "使用弱引用 weakref 避免循环引用",
            "large_data_structures": "考虑使用生成器或分批处理大型数据",
            "memory_intensive_operations": "分块读取大文件，避免一次性加载到内存",
        }
        return fixes.get(issue_type, "优化内存使用")

    def create_memory_profiler(self) -> str:
        """创建内存分析器"""
        logger.info("📊 创建内存分析器...")

        profiler_dir = self.project_root / "src" / "core" / "monitoring"
        profiler_dir.mkdir(parents=True, exist_ok=True)

        profiler_file = profiler_dir / "memory_profiler.py"

        profiler_content = '''"""
索克生活项目 - 内存分析器
监控和分析应用程序的内存使用情况
"""

import gc
import sys
import psutil
import tracemalloc
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from functools import wraps
import time

logger = logging.getLogger(__name__)

@dataclass
class MemorySnapshot:
    """内存快照"""
    timestamp: float
    current_memory: float
    peak_memory: float
    objects_count: int
    gc_collections: Dict[int, int]

class MemoryProfiler:
    """内存分析器"""
    
    def __init__(self):
        self.snapshots: List[MemorySnapshot] = []
        self.tracemalloc_started = False
        self.baseline_snapshot = None
    
    def start_profiling(self):
        """开始内存分析"""
        if not self.tracemalloc_started:
            tracemalloc.start()
            self.tracemalloc_started = True
            logger.info("内存分析已启动")
    
    def stop_profiling(self):
        """停止内存分析"""
        if self.tracemalloc_started:
            tracemalloc.stop()
            self.tracemalloc_started = False
            logger.info("内存分析已停止")
    
    def take_snapshot(self, label: str = None) -> MemorySnapshot:
        """获取内存快照"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        snapshot = MemorySnapshot(
            timestamp=time.time(),
            current_memory=memory_info.rss / 1024 / 1024,  # MB
            peak_memory=memory_info.vms / 1024 / 1024,     # MB
            objects_count=len(gc.get_objects()),
            gc_collections={
                0: gc.get_count()[0],
                1: gc.get_count()[1],
                2: gc.get_count()[2]
            }
        )
        
        self.snapshots.append(snapshot)
        
        if label:
            logger.info(f"内存快照 [{label}]: {snapshot.current_memory:.2f}MB")
        
        return snapshot
    
    def set_baseline(self):
        """设置基线快照"""
        self.baseline_snapshot = self.take_snapshot("baseline")
    
    def get_memory_diff(self) -> Optional[float]:
        """获取与基线的内存差异"""
        if not self.baseline_snapshot or not self.snapshots:
            return None
        
        current = self.snapshots[-1]
        return current.current_memory - self.baseline_snapshot.current_memory
    
    def analyze_memory_leaks(self) -> List[str]:
        """分析内存泄漏"""
        if not self.tracemalloc_started:
            return ["内存分析未启动"]
        
        current, peak = tracemalloc.get_traced_memory()
        top_stats = tracemalloc.take_snapshot().statistics('lineno')
        
        leaks = []
        for stat in top_stats[:10]:
            leaks.append(f"{stat.traceback.format()[-1]}: {stat.size / 1024:.1f} KB")
        
        return leaks
    
    def force_garbage_collection(self) -> Dict[str, int]:
        """强制垃圾回收"""
        before_counts = gc.get_count()
        collected = gc.collect()
        after_counts = gc.get_count()
        
        result = {
            'collected_objects': collected,
            'before_counts': before_counts,
            'after_counts': after_counts
        }
        
        logger.info(f"垃圾回收完成: 回收了 {collected} 个对象")
        return result
    
    def get_memory_report(self) -> str:
        """生成内存报告"""
        if not self.snapshots:
            return "没有内存快照数据"
        
        latest = self.snapshots[-1]
        report = f"""
内存使用报告
============
当前内存使用: {latest.current_memory:.2f} MB
峰值内存使用: {latest.peak_memory:.2f} MB
对象数量: {latest.objects_count:,}
GC统计: Gen0={latest.gc_collections[0]}, Gen1={latest.gc_collections[1]}, Gen2={latest.gc_collections[2]}
"""
        
        if self.baseline_snapshot:
            diff = self.get_memory_diff()
            report += f"与基线差异: {diff:+.2f} MB\\n"
        
        if len(self.snapshots) > 1:
            trend = latest.current_memory - self.snapshots[0].current_memory
            report += f"总体趋势: {trend:+.2f} MB\\n"
        
        return report

# 内存监控装饰器
def memory_monitor(func):
    """内存监控装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = MemoryProfiler()
        profiler.start_profiling()
        profiler.take_snapshot(f"before_{func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            profiler.take_snapshot(f"after_{func.__name__}")
            diff = profiler.get_memory_diff()
            if diff and diff > 10:  # 超过10MB增长
                logger.warning(f"函数 {func.__name__} 内存增长: {diff:.2f}MB")
            profiler.stop_profiling()
    
    return wrapper

# 内存上下文管理器
class MemoryContext:
    """内存监控上下文管理器"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.profiler = MemoryProfiler()
    
    def __enter__(self):
        self.profiler.start_profiling()
        self.profiler.set_baseline()
        return self.profiler
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        final_snapshot = self.profiler.take_snapshot(f"final_{self.operation_name}")
        diff = self.profiler.get_memory_diff()
        
        if diff and diff > 5:  # 超过5MB增长
            logger.warning(f"操作 {self.operation_name} 内存增长: {diff:.2f}MB")
        
        self.profiler.stop_profiling()

# 全局内存分析器实例
global_profiler = MemoryProfiler()
'''

        with open(profiler_file, "w", encoding="utf-8") as f:
            f.write(profiler_content)

        return str(profiler_file)

    def create_memory_optimization_guide(self) -> str:
        """创建内存优化指南"""
        guide_path = (
            self.project_root / "docs" / "development" / "memory_optimization_guide.md"
        )
        guide_path.parent.mkdir(parents=True, exist_ok=True)

        guide_content = """# Python内存优化指南

## 📋 内存管理最佳实践

### 1. 文件操作
```python
# ✅ 推荐 - 使用with语句
with open('file.txt', 'r') as f:
    content = f.read()
# 文件自动关闭

# ❌ 避免 - 手动管理文件
f = open('file.txt', 'r')
content = f.read()
# 可能忘记关闭文件
```

### 2. 大数据处理
```python
# ✅ 推荐 - 使用生成器
def read_large_file(filename):
    with open(filename, 'r') as f:
        for line in f:
            yield line.strip()

# ❌ 避免 - 一次性加载
def read_large_file_bad(filename):
    with open(filename, 'r') as f:
        return f.readlines()  # 占用大量内存
```

### 3. 列表推导式
```python
# ✅ 推荐 - 生成器表达式
data_gen = (x * 2 for x in range(1000000))

# ❌ 避免 - 大型列表推导式
data_list = [x * 2 for x in range(1000000)]  # 占用大量内存
```

### 4. 循环引用
```python
import weakref

class Parent:
    def __init__(self):
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)
        # ✅ 使用弱引用避免循环引用
        child.parent = weakref.ref(self)

class Child:
    def __init__(self):
        self.parent = None
```

### 5. 全局变量
```python
# ❌ 避免 - 全局变量
global_cache = {}

# ✅ 推荐 - 类属性或函数参数
class CacheManager:
    def __init__(self):
        self._cache = {}
    
    def get(self, key):
        return self._cache.get(key)
```

## 🔧 内存监控工具

### 1. 使用内存分析器
```python
from src.core.monitoring.memory_profiler import MemoryContext, memory_monitor

# 上下文管理器
with MemoryContext("data_processing") as profiler:
    # 执行内存密集型操作
    process_large_data()
    print(profiler.get_memory_report())

# 装饰器
@memory_monitor
def expensive_operation():
    # 内存密集型操作
    pass
```

### 2. 手动内存检查
```python
import gc
import psutil

def check_memory():
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"当前内存使用: {memory_mb:.2f} MB")
    
    # 强制垃圾回收
    collected = gc.collect()
    print(f"回收对象数: {collected}")
```

## 🚫 常见内存陷阱

### 1. 未关闭的资源
- 文件句柄
- 数据库连接
- 网络连接
- 线程和进程

### 2. 大型数据结构
- 巨大的列表或字典
- 未清理的缓存
- 累积的日志数据

### 3. 循环引用
- 父子对象相互引用
- 回调函数持有对象引用
- 事件监听器未正确移除

### 4. 内存泄漏模式
```python
# ❌ 泄漏模式1: 全局列表累积
global_list = []
def add_data(data):
    global_list.append(data)  # 永远不清理

# ❌ 泄漏模式2: 闭包持有大对象
def create_handler(large_data):
    def handler():
        # 即使不使用large_data，闭包也会持有引用
        pass
    return handler

# ❌ 泄漏模式3: 缓存无限增长
cache = {}
def get_data(key):
    if key not in cache:
        cache[key] = expensive_operation(key)  # 缓存永远不清理
    return cache[key]
```

## 🎯 优化策略

### 1. 分批处理
```python
def process_large_dataset(data):
    batch_size = 1000
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        process_batch(batch)
        # 批处理完成后，batch会被垃圾回收
```

### 2. 使用__slots__
```python
class OptimizedClass:
    __slots__ = ['x', 'y', 'z']  # 减少内存使用
    
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
```

### 3. 及时清理
```python
def process_data():
    large_data = load_large_dataset()
    result = process(large_data)
    
    # 及时删除大对象
    del large_data
    gc.collect()  # 强制垃圾回收
    
    return result
```

### 4. 使用生成器链
```python
def data_pipeline(filename):
    return (
        transform(line)
        for line in read_file(filename)
        if filter_condition(line)
    )
```

## 📊 内存监控

### 1. 定期检查
- 监控内存使用趋势
- 设置内存使用阈值
- 自动触发垃圾回收

### 2. 性能测试
- 压力测试内存使用
- 长时间运行测试
- 内存泄漏检测

### 3. 生产环境监控
- 实时内存监控
- 内存使用告警
- 自动重启机制
"""

        with open(guide_path, "w", encoding="utf-8") as f:
            f.write(guide_content)

        return str(guide_path)

    def generate_report(self) -> str:
        """生成内存优化报告"""
        logger.info("📊 生成内存优化报告...")

        report = f"""# 内存管理优化报告

## 📊 扫描结果概览

- **扫描文件数量**: {len(self._get_python_files())}
- **发现内存问题**: {len(self.issues_found)}
- **问题类型分布**:
"""

        # 统计问题类型
        issue_types = {}
        severity_count = {}

        for issue in self.issues_found:
            issue_types[issue.issue_type] = issue_types.get(issue.issue_type, 0) + 1
            severity_count[issue.severity] = severity_count.get(issue.severity, 0) + 1

        for issue_type, count in issue_types.items():
            report += f"  - {issue_type}: {count}\n"

        report += "\n- **严重性分布**:\n"
        for severity, count in severity_count.items():
            report += f"  - {severity}: {count}\n"

        report += "\n## 🔍 发现的内存问题详情\n\n"

        # 按严重性分组
        by_severity = {}
        for issue in self.issues_found:
            if issue.severity not in by_severity:
                by_severity[issue.severity] = []
            by_severity[issue.severity].append(issue)

        for severity in ["HIGH", "MEDIUM", "LOW"]:
            if severity in by_severity:
                report += f"### {severity} 严重性\n\n"
                for issue in by_severity[severity]:
                    report += f"**文件**: `{issue.file_path}:{issue.line_number}`\n"
                    report += f"**类型**: {issue.issue_type}\n"
                    report += f"**描述**: {issue.description}\n"
                    report += f"**代码**: `{issue.code_snippet}`\n"
                    report += f"**修复建议**: {issue.suggested_fix}\n\n"

        report += """
## 🛠️ 修复步骤

### 1. 立即修复（高优先级）
1. 修复所有未正确关闭的文件操作
2. 解决循环引用问题
3. 优化大型数据结构的使用

### 2. 中期优化
1. 替换大型列表推导式为生成器
2. 减少全局变量的使用
3. 实施内存监控

### 3. 长期改进
1. 建立内存使用规范
2. 定期进行内存分析
3. 优化算法和数据结构

## 📋 内存优化指南

请参考 `docs/development/memory_optimization_guide.md` 了解详细的内存优化指南。

## ⚠️ 注意事项

1. **文件句柄泄漏**会导致系统资源耗尽
2. **循环引用**会阻止垃圾回收
3. **大型数据结构**会快速消耗内存
4. **全局变量**会持续占用内存直到程序结束
"""

        return report


def main():
    """主函数"""
    project_root = os.getcwd()
    print("🧠 索克生活项目 - 内存管理优化工具")
    print("=" * 60)

    optimizer = MemoryOptimizer(project_root)

    # 1. 扫描内存问题
    issues = optimizer.scan_memory_issues()

    # 2. 创建内存分析器
    profiler_file = optimizer.create_memory_profiler()
    print(f"✅ 已创建内存分析器: {profiler_file}")

    # 3. 创建内存优化指南
    guide_file = optimizer.create_memory_optimization_guide()
    print(f"✅ 已创建内存优化指南: {guide_file}")

    # 4. 生成报告
    report = optimizer.generate_report()

    # 保存报告
    report_file = Path(project_root) / "memory_optimization_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"📊 优化报告已保存到: {report_file}")

    if issues:
        print(f"\n⚠️  发现 {len(issues)} 个内存问题，请查看报告详情")
    else:
        print("\n✅ 未发现内存问题")


if __name__ == "__main__":
    main()
