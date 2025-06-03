#!/usr/bin/env python3
"""
索克生活项目Console.log语句清理脚本
清理所有开发调试用的console.log语句
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

class ConsoleLogCleaner:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.cleaned_files = []
        self.console_log_patterns = [
            r'console\.log\([^)]*\);?\s*',
            r'console\.debug\([^)]*\);?\s*',
            r'console\.info\([^)]*\);?\s*',
            r'console\.warn\([^)]*\);?\s*',
            r'console\.error\([^)]*\);?\s*',
            r'console\.trace\([^)]*\);?\s*',
            r'console\.table\([^)]*\);?\s*',
            r'console\.time\([^)]*\);?\s*',
            r'console\.timeEnd\([^)]*\);?\s*',
        ]
        
    def clean_console_logs(self) -> Dict:
        """清理所有console.log语句"""
        print("🧹 开始清理Console.log语句...")
        
        # 查找所有JavaScript/TypeScript文件
        js_files = []
        for pattern in ["*.js", "*.jsx", "*.ts", "*.tsx"]:
            js_files.extend(self.project_root.rglob(pattern))
        
        # 过滤掉不需要的文件
        js_files = [f for f in js_files if not self._should_skip_file(f)]
        
        print(f"找到 {len(js_files)} 个JavaScript/TypeScript文件需要清理...")
        
        total_removed = 0
        for file_path in js_files:
            removed_count = self._clean_file_console_logs(file_path)
            if removed_count > 0:
                self.cleaned_files.append(str(file_path))
                total_removed += removed_count
        
        # 生成报告
        report = self._generate_report(total_removed)
        
        return {
            'total_files_processed': len(js_files),
            'files_cleaned': len(self.cleaned_files),
            'total_console_logs_removed': total_removed,
            'report': report
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
            'ios/build'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def _clean_file_console_logs(self, file_path: Path) -> int:
        """清理单个文件的console.log语句"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            removed_count = 0
            
            # 应用所有console.log清理模式
            for pattern in self.console_log_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                removed_count += len(matches)
                content = re.sub(pattern, '', content, flags=re.MULTILINE)
            
            # 清理空行
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            # 如果内容有变化，保存文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 已清理 {removed_count} 个console.log: {file_path}")
                return removed_count
            
            return 0
            
        except Exception as e:
            print(f"❌ 清理失败 {file_path}: {e}")
            return 0
    
    def _generate_report(self, total_removed: int) -> str:
        """生成清理报告"""
        report = f"""# 🧹 Console.log语句清理报告

**清理时间**: {os.popen('date').read().strip()}
**项目路径**: {self.project_root}

## 📊 清理统计

- 清理的文件数量: {len(self.cleaned_files)}
- 移除的console.log语句: {total_removed}
- 清理的模式类型: {len(self.console_log_patterns)}

## 🔧 清理的Console语句类型

1. console.log() - 普通日志输出
2. console.debug() - 调试信息
3. console.info() - 信息输出
4. console.warn() - 警告信息
5. console.error() - 错误信息
6. console.trace() - 堆栈跟踪
7. console.table() - 表格输出
8. console.time() - 计时开始
9. console.timeEnd() - 计时结束

## 📁 清理的文件列表

"""
        
        for i, file_path in enumerate(self.cleaned_files, 1):
            report += f"{i}. {file_path}\n"
        
        report += f"""
## 📈 预期效果

通过Console.log语句清理，预期：
- 生产环境代码更加干净
- 减少不必要的输出
- 提升应用性能
- 改善代码质量评分

## 🎯 建议

1. 在开发过程中使用专门的日志库
2. 建立代码审查机制防止console.log进入生产环境
3. 使用ESLint规则自动检测console语句
4. 在CI/CD流程中集成console.log检查

"""
        
        return report

def main():
    print("🧹 开始Console.log语句清理...")
    
    cleaner = ConsoleLogCleaner('.')
    
    # 执行清理
    result = cleaner.clean_console_logs()
    
    # 保存报告
    with open('console_log_cleanup_report.md', 'w', encoding='utf-8') as f:
        f.write(result['report'])
    
    print(f"✅ Console.log清理完成！")
    print(f"📊 处理文件: {result['total_files_processed']}")
    print(f"📊 清理文件: {result['files_cleaned']}")
    print(f"📊 移除语句: {result['total_console_logs_removed']}")
    print(f"📄 报告已保存到: console_log_cleanup_report.md")

if __name__ == '__main__':
    main() 