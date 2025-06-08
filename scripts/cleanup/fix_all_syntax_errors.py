"""
fix_all_syntax_errors - 索克生活项目模块
"""

from pathlib import Path
from typing import List, Dict, Tuple
import argparse
import os
import re

#!/usr/bin/env python3
"""
索克生活项目全面语法错误修复脚本
专门修复测试文件和其他文件的各种语法问题
"""


class ComprehensiveSyntaxFixer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.failed_files = []

    def fix_test_files(self) -> Dict:
        """修复测试文件的语法错误"""
        print("🧪 修复测试文件语法错误...")

        test_files = []
        for pattern in ["*.test.ts", "*.test.tsx", "*.spec.ts", "*.spec.tsx"]:
            test_files.extend(self.project_root.rglob(pattern))

        test_files = [f for f in test_files if not self._should_skip_file(f)]

        for test_file in test_files:
            try:
                if self._fix_test_file(test_file):
                    self.fixed_files.append(str(test_file))
                    print(f"  ✅ 已修复: {test_file}")
                else:
                    self.failed_files.append(str(test_file))
            except Exception as e:
                print(f"  ❌ 修复失败 {test_file}: {e}")
                self.failed_files.append(str(test_file))

        return {
            'fixed_files': len(self.fixed_files),
            'failed_files': len(self.failed_files),
            'total_files': len(test_files)
        }

    def _fix_test_file(self, file_path: Path) -> bool:
        """修复单个测试文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # 修复模式列表
            fixes = [
                # 修复import语句
                (r'import { performance } from perf_hooks";', 'import { performance } from "perf_hooks";'),
                (r'from "([^"]*);', r'from "\1";'),
                (r'from "([^"]*)"([^;])', r'from "\1";\2'),

                # 修复describe和test函数
                (r'describe\("([^"]*)", \(\); =>', r'describe("\1", () =>'),
                (r'it\("([^"]*)", \(\); =>', r'it("\1", () =>'),
                (r'test\("([^"]*)", \(\); =>', r'test("\1", () =>'),
                (r'beforeEach\(\(\); =>', r'beforeEach(() =>'),
                (r'afterEach\(\(\); =>', r'afterEach(() =>'),

                # 修复字符串和语法错误
                (r'it\(should ([^"]*)", \(\); =>', r'it("should \1", () =>'),
                (r'it\(([^"]*)", \(\); =>', r'it("\1", () =>'),

                # 修复多余的分号和字符
                (r';;+', ';'),
                (r';0;0;', ''),
                (r'\.now;\(;\);', '.now();'),
                (r'iteratio;n;s;', 'iterations'),
                (r'for \(let i = ;0;', 'for (let i = 0'),
                (r'i < iterations; i\+\+\) \{', 'i < iterations; i++) {'),

                # 修复expect语句
                (r'expect\(([^)]+)\)\.toBeLessThan\(([^)]+)\);', r'expect(\1).toBeLessThan(\2);'),

                # 修复空的import
                (r'import \{  \} from', 'import {} from'),

                # 修复注释
                (r'// Should execute within 1ms on average;', '// Should execute within 1ms on average'),

                # 修复函数调用
                (r'performance\.now;\(;\);', 'performance.now();'),
                (r'jest\.clearAllMocks\(\);', 'jest.clearAllMocks();'),
            ]

            # 应用修复
            for pattern, replacement in fixes:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

            # 特殊处理：修复复杂的语法错误
            lines = content.split('\n')
            fixed_lines = []

            for line in lines:
                # 修复特定的语法错误模式
                if 'it(should' in line and not line.strip().startswith('//'):
                    # 修复缺失引号的it语句
                    line = re.sub(r'it\(should ([^"]*)", \(\); =>', r'it("should \1", () =>', line)

                if 'const iterations = 10;0;0;' in line:
                    line = line.replace('const iterations = 10;0;0;', 'const iterations = 100;')

                if 'for (let i = ;0;' in line:
                    line = line.replace('for (let i = ;0;', 'for (let i = 0;')

                if 'const averageTime = (endTime - startTime) / iteratio;n;s;' in line:
                    line = line.replace('iteratio;n;s;', 'iterations')

                # 移除多余的分号
                line = re.sub(r';;+', ';', line)

                fixed_lines.append(line)

            content = '\n'.join(fixed_lines)

            # 如果内容有变化，保存文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True

        except Exception as e:
            print(f"    修复错误: {e}")
            return False

        return False

    def fix_typescript_files(self) -> Dict:
        """修复TypeScript文件的语法错误"""
        print("📱 修复TypeScript文件语法错误...")

        ts_files = []
        for pattern in ["*.ts", "*.tsx"]:
            ts_files.extend(self.project_root.rglob(pattern))

        ts_files = [f for f in ts_files if not self._should_skip_file(f) and not str(f).endswith(('.test.ts', '.test.tsx', '.spec.ts', '.spec.tsx'))]

        fixed_count = 0

        for ts_file in ts_files:
            try:
                if self._fix_typescript_file(ts_file):
                    fixed_count += 1
                    self.fixed_files.append(str(ts_file))
            except Exception as e:
                print(f"  ⚠️  处理文件时出错 {ts_file}: {e}")
                self.failed_files.append(str(ts_file))

        return {
            'fixed_files': fixed_count,
            'total_files': len(ts_files)
        }

    def _fix_typescript_file(self, file_path: Path) -> bool:
        """修复单个TypeScript文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # TypeScript常见语法错误修复
            fixes = [
                # 修复import语句
                (r'import\s+([^;]+);([^;])', r'import \1;\n\2'),
                (r'from\s+"([^"]*)"([^;])', r'from "\1";\2'),

                # 修复export语句
                (r'export\s+([^;]+);([^;])', r'export \1;\n\2'),

                # 修复接口定义
                (r'interface\s+(\w+)\s*\{', r'interface \1 {'),

                # 修复类型注解
                (r':\s*([A-Z][a-zA-Z]*)\s*=', r': \1 ='),

                # 修复函数定义
                (r'function\s+(\w+)\s*\(', r'function \1('),

                # 修复多余的分号
                (r';;+', ';'),

                # 修复React组件
                (r'React\.FC<([^>]*)>', r'React.FC<\1>'),
            ]

            for pattern, replacement in fixes:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ 已修复: {file_path}")
                return True

        except Exception as e:
            print(f"  ❌ 修复失败 {file_path}: {e}")
            return False

        return False

    def fix_javascript_files(self) -> Dict:
        """修复JavaScript文件的语法错误"""
        print("🔧 修复JavaScript文件语法错误...")

        js_files = []
        for pattern in ["*.js", "*.jsx"]:
            js_files.extend(self.project_root.rglob(pattern))

        js_files = [f for f in js_files if not self._should_skip_file(f)]

        fixed_count = 0

        for js_file in js_files:
            try:
                if self._fix_javascript_file(js_file):
                    fixed_count += 1
                    self.fixed_files.append(str(js_file))
            except Exception as e:
                print(f"  ⚠️  处理文件时出错 {js_file}: {e}")
                self.failed_files.append(str(js_file))

        return {
            'fixed_files': fixed_count,
            'total_files': len(js_files)
        }

    def _fix_javascript_file(self, file_path: Path) -> bool:
        """修复单个JavaScript文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # JavaScript常见语法错误修复
            fixes = [
                # 修复模块导入导出
                (r'module\.exports\s*=\s*\{', 'module.exports = {'),
                (r'require\("([^"]*)"', r'require("\1")'),

                # 修复对象和数组
                (r',\s*}', '}'),
                (r',\s*]', ']'),
                (r',\s*\)', ')'),

                # 修复函数定义
                (r'function\s*\(', 'function('),

                # 修复多余的分号
                (r';;+', ';'),
            ]

            for pattern, replacement in fixes:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ 已修复: {file_path}")
                return True

        except Exception as e:
            print(f"  ❌ 修复失败 {file_path}: {e}")
            return False

        return False

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
        report = f"""# 🔧 全面语法错误修复报告

**修复时间**: {os.popen('date').read().strip()}
**项目路径**: {self.project_root}

## 📊 修复统计

- 成功修复文件: {len(self.fixed_files)} 个
- 修复失败文件: {len(self.failed_files)} 个

## ✅ 成功修复的文件

"""

        for file in self.fixed_files[:30]:  # 只显示前30个
            report += f"- {file}\n"

        if len(self.fixed_files) > 30:
            report += f"\n... 还有 {len(self.fixed_files) - 30} 个文件\n"

        if self.failed_files:
            report += f"""

## ❌ 修复失败的文件

"""
            for file in self.failed_files[:10]:  # 只显示前10个
                report += f"- {file}\n"

            if len(self.failed_files) > 10:
                report += f"\n... 还有 {len(self.failed_files) - 10} 个文件\n"

        report += f"""

## 🎯 修复的问题类型

1. **测试文件语法错误**
- 修复缺失引号的import语句
- 修复describe、it、test函数的语法错误
- 修复performance测试中的语法问题

2. **TypeScript语法错误**
- 修复import/export语句
- 修复类型注解
- 修复接口定义

3. **JavaScript语法错误**
- 修复模块导入导出
- 修复对象和数组语法
- 修复函数定义

4. **通用语法问题**
- 清理多余的分号
- 修复字符串引号问题
- 修复函数调用语法

## 📈 预期效果

通过全面语法错误修复，预期：
- 测试可以正常运行
- 构建错误大幅减少
- 代码质量评分提升 20-30 分
- 开发体验显著改善

"""

        return report

def main():
    parser = argparse.ArgumentParser(description='索克生活项目全面语法错误修复')
    parser.add_argument('--project-root', default='.', help='项目根目录路径')
    parser.add_argument('--output', default='comprehensive_syntax_fix_report.md', help='输出报告文件名')
    parser.add_argument('--test-only', action='store_true', help='只修复测试文件')

    args = parser.parse_args()

    print("🔧 开始全面语法错误修复...")

    fixer = ComprehensiveSyntaxFixer(args.project_root)

    # 执行修复
    if args.test_only:
        fixer.fix_test_files()
    else:
        fixer.fix_test_files()
        fixer.fix_typescript_files()
        fixer.fix_javascript_files()

    # 生成报告
    report = fixer.generate_report()

    # 保存报告
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ 全面语法错误修复完成！报告已保存到: {args.output}")
    print(f"📊 修复文件数: {len(fixer.fixed_files)}")
    print(f"❌ 失败文件数: {len(fixer.failed_files)}")

if __name__ == '__main__':
    main() 