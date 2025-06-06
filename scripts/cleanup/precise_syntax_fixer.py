"""
precise_syntax_fixer - 索克生活项目模块
"""

from pathlib import Path
from typing import List, Dict, Tuple
import argparse
import os
import re

#!/usr/bin/env python3
"""
索克生活项目精准语法错误修复脚本
专门处理TypeScript解析器错误和复杂语法问题
"""


class PreciseSyntaxFixer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.failed_files = []
        
    def fix_critical_syntax_errors(self) -> Dict:
        """修复关键的语法错误"""
        print("🎯 修复关键语法错误...")
        
        # 重点修复的文件模式
        critical_patterns = [
            "*.test.ts",
            "*.test.tsx", 
            "*.spec.ts",
            "*.spec.tsx",
            "src/App.tsx",
            "src/index.js",
            "babel.config.js",
            "jest.config.js",
            ".eslintrc.js"
        ]
        
        critical_files = []
        for pattern in critical_patterns:
            critical_files.extend(self.project_root.rglob(pattern))
        
        critical_files = [f for f in critical_files if not self._should_skip_file(f)]
        
        for file_path in critical_files:
            try:
                if self._fix_critical_file(file_path):
                    self.fixed_files.append(str(file_path))
                    print(f"  ✅ 已修复: {file_path}")
                else:
                    self.failed_files.append(str(file_path))
            except Exception as e:
                print(f"  ❌ 修复失败 {file_path}: {e}")
                self.failed_files.append(str(file_path))
        
        return {
            'fixed_files': len(self.fixed_files),
            'failed_files': len(self.failed_files),
            'total_files': len(critical_files)
        }
    
    def _fix_critical_file(self, file_path: Path) -> bool:
        """修复单个关键文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 根据文件类型应用不同的修复策略
            if str(file_path).endswith(('.test.ts', '.test.tsx', '.spec.ts', '.spec.tsx')):
                content = self._fix_test_file_content(content)
            elif str(file_path).endswith('.tsx'):
                content = self._fix_tsx_file_content(content)
            elif str(file_path).endswith('.ts'):
                content = self._fix_ts_file_content(content)
            elif str(file_path).endswith('.js'):
                content = self._fix_js_file_content(content)
            
            # 如果内容有变化，保存文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
        except Exception as e:
            print(f"    修复错误: {e}")
            return False
        
        return False
    
    def _fix_test_file_content(self, content: str) -> str:
        """修复测试文件内容"""
        # 修复测试文件的常见语法错误
        fixes = [
            # 修复import语句
            (r'import { performance } from perf_hooks";', 'import { performance } from "perf_hooks";'),
            (r'import\s+([^;]+)from\s+"([^"]*)"([^;])', r'import \1 from "\2";\3'),
            (r'from\s+"([^"]*)"([^;])', r'from "\1";\2'),
            
            # 修复describe和test函数
            (r'describe\s*\(\s*"([^"]*)",\s*\(\)\s*;\s*=>', r'describe("\1", () =>'),
            (r'it\s*\(\s*"([^"]*)",\s*\(\)\s*;\s*=>', r'it("\1", () =>'),
            (r'test\s*\(\s*"([^"]*)",\s*\(\)\s*;\s*=>', r'test("\1", () =>'),
            (r'beforeEach\s*\(\s*\(\)\s*;\s*=>', r'beforeEach(() =>'),
            (r'afterEach\s*\(\s*\(\)\s*;\s*=>', r'afterEach(() =>'),
            
            # 修复expect语句
            (r'expect\s*\(\s*([^)]+)\s*\)\s*\.\s*toBe\s*\(\s*([^)]+)\s*\)\s*;', r'expect(\1).toBe(\2);'),
            (r'expect\s*\(\s*([^)]+)\s*\)\s*\.\s*toEqual\s*\(\s*([^)]+)\s*\)\s*;', r'expect(\1).toEqual(\2);'),
            
            # 修复性能测试
            (r'performance\.now\s*;\s*\(\s*;\s*\);', 'performance.now();'),
            (r'const\s+iterations\s*=\s*10\s*;\s*0\s*;\s*0\s*;', 'const iterations = 100;'),
            (r'for\s*\(\s*let\s+i\s*=\s*;\s*0\s*;', 'for (let i = 0;'),
            (r'iteratio\s*;\s*n\s*;\s*s\s*;', 'iterations'),
            
            # 修复多余的分号和字符
            (r';\s*;\s*;+', ';'),
            (r';\s*0\s*;\s*0\s*;', ''),
            
            # 修复字符串问题
            (r'it\s*\(\s*should\s+([^"]*)",\s*\(\)\s*;\s*=>', r'it("should \1", () =>'),
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        return content
    
    def _fix_tsx_file_content(self, content: str) -> str:
        """修复TSX文件内容"""
        fixes = [
            # 修复React导入
            (r'import\s+React\s+from\s+"react"([^;])', r'import React from "react";\1'),
            (r'import\s+\{\s*([^}]+)\s*\}\s+from\s+"react"([^;])', r'import { \1 } from "react";\2'),
            
            # 修复React Native导入
            (r'import\s+\{\s*([^}]+)\s*\}\s+from\s+"react-native"([^;])', r'import { \1 } from "react-native";\2'),
            
            # 修复组件定义
            (r'const\s+(\w+):\s*React\.FC<([^>]*)>\s*=\s*\(\s*([^)]*)\s*\)\s*=>', r'const \1: React.FC<\2> = (\3) =>'),
            
            # 修复JSX语法
            (r'<([A-Z]\w*)\s+([^>]*)/>', r'<\1 \2 />'),
            (r'<([A-Z]\w*)\s*>', r'<\1>'),
            
            # 修复export语句
            (r'export\s+default\s+(\w+)([^;])', r'export default \1;\2'),
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        return content
    
    def _fix_ts_file_content(self, content: str) -> str:
        """修复TS文件内容"""
        fixes = [
            # 修复接口定义
            (r'interface\s+(\w+)\s*\{', r'interface \1 {'),
            (r'export\s+interface\s+(\w+)\s*\{', r'export interface \1 {'),
            
            # 修复类型定义
            (r'type\s+(\w+)\s*=\s*([^;]+)([^;])', r'type \1 = \2;\3'),
            (r'export\s+type\s+(\w+)\s*=\s*([^;]+)([^;])', r'export type \1 = \2;\3'),
            
            # 修复函数定义
            (r'function\s+(\w+)\s*\(\s*([^)]*)\s*\):\s*([^{]+)\s*\{', r'function \1(\2): \3 {'),
            (r'export\s+function\s+(\w+)\s*\(\s*([^)]*)\s*\):\s*([^{]+)\s*\{', r'export function \1(\2): \3 {'),
            
            # 修复箭头函数
            (r'const\s+(\w+)\s*=\s*\(\s*([^)]*)\s*\):\s*([^=]+)\s*=>', r'const \1 = (\2): \3 =>'),
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        return content
    
    def _fix_js_file_content(self, content: str) -> str:
        """修复JS文件内容"""
        fixes = [
            # 修复模块导出
            (r'module\.exports\s*=\s*\{', 'module.exports = {'),
            (r'exports\.(\w+)\s*=\s*([^;]+)([^;])', r'exports.\1 = \2;\3'),
            
            # 修复require语句
            (r'const\s+(\w+)\s*=\s*require\s*\(\s*"([^"]*)"([^;])', r'const \1 = require("\2");\3'),
            
            # 修复对象语法
            (r',\s*}', '}'),
            (r',\s*]', ']'),
            
            # 修复函数定义
            (r'function\s+(\w+)\s*\(\s*([^)]*)\s*\)\s*\{', r'function \1(\2) {'),
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        return content
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过某个文件"""
        skip_patterns = [
            'node_modules',
            'venv',
            '.venv',
            '__pycache__',
            '.git',
            'build',
            'dist',
            '.expo',
            'ios/Pods',
            'android/build',
            '.jest-cache',
            'coverage',
            'cleanup_backup',
            'quality_enhancement'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def generate_report(self) -> str:
        """生成修复报告"""
        report = f"""# 🎯 精准语法错误修复报告

**修复时间**: {os.popen('date').read().strip()}
**项目路径**: {self.project_root}

## 📊 修复统计

- 成功修复文件: {len(self.fixed_files)} 个
- 修复失败文件: {len(self.failed_files)} 个

## ✅ 成功修复的文件

"""
        
        for file in self.fixed_files:
            report += f"- {file}\n"
        
        if self.failed_files:
            report += f"""

## ❌ 修复失败的文件

"""
            for file in self.failed_files:
                report += f"- {file}\n"
        
        report += f"""

## 🔧 修复的问题类型

1. **测试文件关键错误**
   - 修复describe、it、test函数的语法错误
   - 修复import语句的引号问题
   - 修复性能测试中的语法问题
   - 修复expect断言语法

2. **TypeScript语法错误**
   - 修复接口和类型定义
   - 修复函数签名
   - 修复箭头函数语法

3. **React/TSX语法错误**
   - 修复React组件导入
   - 修复JSX语法
   - 修复组件定义

4. **JavaScript配置文件**
   - 修复模块导入导出
   - 修复对象语法
   - 修复函数定义

## 📈 预期效果

通过精准语法错误修复，预期：
- 测试可以正常运行
- TypeScript编译错误消除
- 构建过程顺利进行
- 代码质量评分提升

"""
        
        return report

def main():
    parser = argparse.ArgumentParser(description='索克生活项目精准语法错误修复')
    parser.add_argument('--project-root', default='.', help='项目根目录路径')
    parser.add_argument('--output', default='precise_syntax_fix_report.md', help='输出报告文件名')
    
    args = parser.parse_args()
    
    print("🎯 开始精准语法错误修复...")
    
    fixer = PreciseSyntaxFixer(args.project_root)
    
    # 执行修复
    fixer.fix_critical_syntax_errors()
    
    # 生成报告
    report = fixer.generate_report()
    
    # 保存报告
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 精准语法错误修复完成！报告已保存到: {args.output}")
    print(f"📊 修复文件数: {len(fixer.fixed_files)}")
    print(f"❌ 失败文件数: {len(fixer.failed_files)}")

if __name__ == '__main__':
    main() 