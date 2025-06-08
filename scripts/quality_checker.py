#!/usr/bin/env python3
"""
索克生活项目质量检查器
"""

import subprocess
import sys
import json
from pathlib import Path
import time

class QualityChecker:
    def __init__(self):
        self.project_root = Path.cwd()
        self.results = {}
        
    def run_all_checks(self):
        """运行所有质量检查"""
        print('🔍 启动代码质量检查...')
        
        start_time = time.time()
        
        # Python检查
        self._check_python_quality()
        
        # 生成报告
        end_time = time.time()
        self._generate_quality_report(end_time - start_time)
        
    def _check_python_quality(self):
        """检查Python代码质量"""
        print('🐍 检查Python代码质量...')
        
        # 语法检查
        python_files = list(Path('src').rglob('*.py')) + list(Path('services').rglob('*.py'))
        syntax_errors = 0
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(py_file), 'exec')
            except SyntaxError:
                syntax_errors += 1
                
        self.results['python'] = {
            'total_files': len(python_files),
            'syntax_errors': syntax_errors,
            'syntax_score': ((len(python_files) - syntax_errors) / len(python_files) * 100) if python_files else 0
        }
            
    def _generate_quality_report(self, total_time: float):
        """生成质量报告"""
        print('\n📋 生成质量检查报告...')
        
        syntax_score = self.results.get('python', {}).get('syntax_score', 0)
        
        report_content = f"""# 索克生活项目质量检查报告

## 📊 检查概览

**检查时间**: {time.strftime("%Y-%m-%d %H:%M:%S")}  
**检查耗时**: {total_time:.2f}秒  
**语法正确率**: {syntax_score:.1f}%  

## 🐍 Python代码质量

- **总文件数**: {self.results.get('python', {}).get('total_files', 0)}
- **语法错误**: {self.results.get('python', {}).get('syntax_errors', 0)}
- **语法正确率**: {syntax_score:.1f}%

## 📈 质量改进建议

### 立即改进
- 修复语法错误
- 安装代码格式化工具
- 建立自动化检查流程

---

**报告生成时间**: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        with open('QUALITY_CHECK_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        print(f'📋 质量检查报告已保存到: QUALITY_CHECK_REPORT.md')
        print(f'📊 语法正确率: {syntax_score:.1f}%')

def main():
    checker = QualityChecker()
    checker.run_all_checks()

if __name__ == "__main__":
    main()
