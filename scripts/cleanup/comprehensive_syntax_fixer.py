"""
comprehensive_syntax_fixer - 索克生活项目模块
"""

from pathlib import Path
from typing import List, Dict, Tuple
import ast
import os
import re

#!/usr/bin/env python3
"""
索克生活项目综合语法错误修复脚本
处理所有剩余的语法错误
"""


class ComprehensiveSyntaxFixer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.failed_files = []

    def fix_python_syntax_errors(self) -> int:
        """修复Python语法错误"""
        print("🐍 修复Python语法错误...")

        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]

        fixed_count = 0
        for file_path in python_files:
            try:
                if self._fix_python_file(file_path):
                    fixed_count += 1
                    self.fixed_files.append(str(file_path))
            except Exception as e:
                self.failed_files.append(str(file_path))

        return fixed_count

    def fix_typescript_syntax_errors(self) -> int:
        """修复TypeScript语法错误"""
        print("📱 修复TypeScript语法错误...")

        ts_files = []
        for pattern in ["*.ts", "*.tsx"]:
            ts_files.extend(self.project_root.rglob(pattern))

        ts_files = [f for f in ts_files if not self._should_skip_file(f)]

        fixed_count = 0
        for file_path in ts_files:
            try:
                if self._fix_typescript_file(file_path):
                    fixed_count += 1
                    self.fixed_files.append(str(file_path))
            except Exception as e:
                self.failed_files.append(str(file_path))

        return fixed_count

    def _fix_python_file(self, file_path: Path) -> bool:
        """修复单个Python文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # 检查语法是否正确
            try:
                ast.parse(content)
                return False  # 语法已经正确，无需修复
            except SyntaxError:
                pass  # 有语法错误，继续修复

            # 修复常见的Python语法错误
            content = self._fix_python_syntax(content)

            # 再次检查语法
            try:
                ast.parse(content)
                # 语法正确，保存文件
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    return True
            except SyntaxError:
                pass  # 仍有语法错误

        except Exception:
            pass

        return False

    def _fix_typescript_file(self, file_path: Path) -> bool:
        """修复单个TypeScript文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # 修复常见的TypeScript语法错误
            content = self._fix_typescript_syntax(content)

            # 如果内容有变化，保存文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True

        except Exception:
            pass

        return False

    def _fix_python_syntax(self, content: str) -> str:
        """修复Python语法错误"""
        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            # 修复缺失的冒号
            if re.match(r'^\s*(if|elif|else|for|while|def|class|try|except|finally|with)\s+.*[^:]$', line.strip()):
                if not line.strip().endswith(':'):
                    line = line.rstrip() + ':'

            # 修复缺失的引号
            line = re.sub(r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+from\s+([a-zA-Z_][a-zA-Z0-9_./]*)', r'import \1 from "\2"', line)

            # 修复缺失的括号
            if 'print ' in line and not 'print(' in line:
                line = re.sub(r'print\s+(.+)', r'print(\1)', line)

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _fix_typescript_syntax(self, content: str) -> str:
        """修复TypeScript语法错误"""
        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            # 修复import语句缺失引号
            line = re.sub(r'import\s+([^"\']+)\s+from\s+([a-zA-Z_][a-zA-Z0-9_./\-@]*)', r'import \1 from "\2"', line)

            # 修复export语句缺失引号
            line = re.sub(r'export\s+([^"\']+)\s+from\s+([a-zA-Z_][a-zA-Z0-9_./\-@]*)', r'export \1 from "\2"', line)

            # 修复缺失的分号
            if (line.strip().startswith('const ') or 
                line.strip().startswith('let ') or 
                line.strip().startswith('var ')) and '=' in line and not line.strip().endswith(';'):
                line = line.rstrip() + ';'

            # 修复expect语句缺失分号
            if 'expect(' in line and line.strip().endswith(')') and not line.strip().endswith(');'):
                if any(method in line for method in ['.toBe(', '.toEqual(', '.toBeLessThan(', '.toBeGreaterThan(']):
                    line = line.rstrip() + ';'

            # 修复函数调用缺失分号
            if any(call in line for call in ['performance.now()', 'jest.clearAllMocks()', 'global.gc()']) and not line.strip().endswith(';'):
                line = line.rstrip() + ';'

            # 修复describe和it函数语法
            if line.strip().startswith('describe(') or line.strip().startswith('it('):
                if not line.strip().endswith('{') and not line.strip().endswith(') => {'):
                    # 确保describe和it函数有正确的回调函数语法
                    if line.strip().endswith(')'):
                        line = line.rstrip() + ' => {'

            # 修复for循环语法
            if 'for (let i = 0; i < ' in line and not line.strip().endswith(') {'):
                line = re.sub(r'for\s*\(\s*let\s+i\s*=\s*0\s*;\s*i\s*<\s*([^;]+)\s*;\s*i\+\+\s*\)', r'for (let i = 0; i < \1; i++)', line)
                if not line.strip().endswith('{'):
                    line = line.rstrip() + ' {'

            # 修复if语句语法
            if line.strip().startswith('if (') and not line.strip().endswith('{'):
                if line.strip().endswith(')'):
                    line = line.rstrip() + ' {'

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = [
            'node_modules',
            '.git',
            '__pycache__',
            '.pytest_cache',
            'venv',
            'env',
            '.venv',
            'build',
            'dist',
            '.next',
            'coverage',
            'htmlcov',
            'Pods',
            'android/app/build',
            'ios/build'
        ]

        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)

    def fix_specific_syntax_errors(self) -> int:
        """修复特定的语法错误"""
        print("🎯 修复特定语法错误...")

        # 修复报告中提到的特定文件
        specific_files = [
            'services/suoke-bench-service/internal/suokebench/evaluator.py',
            'services/med-knowledge/app/services/knowledge_service.py',
            'services/accessibility-service/accessibility_service/internal/model/health_data.py',
            'services/rag-service/internal/service/intelligent_tcm_constitution_engine.py',
            'services/rag-service/cmd/server/main.py'
        ]

        fixed_count = 0
        for file_path in specific_files:
            if os.path.exists(file_path):
                try:
                    if self._fix_python_file(Path(file_path)):
                        fixed_count += 1
                        print(f"  ✅ 已修复: {file_path}")
                except Exception as e:
                    print(f"  ❌ 修复失败 {file_path}: {e}")

        return fixed_count

    def run_comprehensive_fix(self) -> Dict:
        """运行综合修复"""
        print("🔧 开始综合语法错误修复...")

        # 修复Python语法错误
        python_fixed = self.fix_python_syntax_errors()

        # 修复TypeScript语法错误
        ts_fixed = self.fix_typescript_syntax_errors()

        # 修复特定语法错误
        specific_fixed = self.fix_specific_syntax_errors()

        return {
            'python_fixed': python_fixed,
            'typescript_fixed': ts_fixed,
            'specific_fixed': specific_fixed,
            'total_fixed': len(self.fixed_files),
            'total_failed': len(self.failed_files)
        }

    def generate_report(self, results: Dict) -> str:
        """生成修复报告"""
        report = f"""# 🔧 综合语法错误修复报告

**修复时间**: {os.popen('date').read().strip()}
**项目路径**: {self.project_root}

## 📊 修复统计

- Python文件修复: {results['python_fixed']} 个
- TypeScript文件修复: {results['typescript_fixed']} 个
- 特定文件修复: {results['specific_fixed']} 个
- 总计修复文件: {results['total_fixed']} 个
- 修复失败文件: {results['total_failed']} 个

## ✅ 成功修复的文件

"""

        for file in self.fixed_files[:20]:  # 只显示前20个
            report += f"- {file}\n"

        if len(self.fixed_files) > 20:
            report += f"... 还有 {len(self.fixed_files) - 20} 个文件\n"

        if self.failed_files:
            report += f"""

## ❌ 修复失败的文件

"""
            for file in self.failed_files[:10]:  # 只显示前10个
                report += f"- {file}\n"

            if len(self.failed_files) > 10:
                report += f"... 还有 {len(self.failed_files) - 10} 个文件\n"

        report += f"""

## 🔧 修复的问题类型

### Python语法错误
1. 缺失的冒号（if、for、def等语句）
2. 缺失的引号（import语句）
3. 缺失的括号（print语句）

### TypeScript语法错误
1. import/export语句缺失引号
2. 变量声明缺失分号
3. expect语句缺失分号
4. 函数调用缺失分号
5. describe/it函数语法错误
6. for循环和if语句语法错误

### 特定文件修复
1. 服务文件的语法错误
2. 配置文件的语法错误
3. 测试文件的语法错误

## 📈 预期效果

通过综合语法错误修复，预期：
- 大幅减少语法错误数量
- 提高代码质量评分
- 改善开发体验
- 减少编译错误

"""

        return report

def main():
    print("🔧 开始综合语法错误修复...")

    fixer = ComprehensiveSyntaxFixer('.')

    # 执行修复
    results = fixer.run_comprehensive_fix()

    # 生成报告
    report = fixer.generate_report(results)

    # 保存报告
    with open('comprehensive_syntax_fix_report.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ 综合语法错误修复完成！")
    print(f"🐍 Python文件修复: {results['python_fixed']}")
    print(f"📱 TypeScript文件修复: {results['typescript_fixed']}")
    print(f"🎯 特定文件修复: {results['specific_fixed']}")
    print(f"📊 总计修复文件: {results['total_fixed']}")
    print(f"❌ 修复失败文件: {results['total_failed']}")
    print(f"📄 报告已保存到: comprehensive_syntax_fix_report.md")

if __name__ == '__main__':
    main() 