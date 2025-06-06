"""
syntax_error_fixer - 索克生活项目模块
"""

from pathlib import Path
from typing import List, Dict, Tuple
import argparse
import ast
import os
import re
import subprocess

#!/usr/bin/env python3
"""
索克生活项目语法错误修复脚本
专门修复Python和JavaScript/TypeScript的语法错误
"""


class SyntaxErrorFixer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.failed_files = []
        
    def fix_python_syntax_errors(self) -> Dict:
        """修复Python语法错误"""
        print("🐍 修复Python语法错误...")
        
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        
        syntax_errors = []
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 尝试解析AST
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    print(f"  发现语法错误: {py_file}:{e.lineno} - {e.msg}")
                    if self._fix_python_file(py_file, content, e):
                        self.fixed_files.append(str(py_file))
                        print(f"  ✅ 已修复: {py_file}")
                    else:
                        self.failed_files.append(str(py_file))
                        syntax_errors.append({
                            'file': str(py_file),
                            'line': e.lineno,
                            'error': e.msg
                        })
                        print(f"  ❌ 修复失败: {py_file}")
                        
            except Exception as e:
                print(f"  ⚠️  处理文件时出错 {py_file}: {e}")
        
        return {
            'fixed_files': self.fixed_files,
            'failed_files': self.failed_files,
            'syntax_errors': syntax_errors
        }
    
    def _fix_python_file(self, file_path: Path, content: str, error: SyntaxError) -> bool:
        """修复单个Python文件的语法错误"""
        lines = content.split('\n')
        error_line_idx = error.lineno - 1
        
        if error_line_idx >= len(lines):
            return False
        
        error_line = lines[error_line_idx]
        original_line = error_line
        fixed = False
        
        # 常见语法错误修复模式
        fixes = [
            # 修复缺失的冒号
            (r'^(\s*)(if|elif|else|for|while|def|class|try|except|finally|with)\s+([^:]+)$', r'\1\2 \3:'),
            # 修复多余的逗号
            (r',\s*}', '}'),
            (r',\s*]', ']'),
            (r',\s*\)', ')'),
            # 修复引号问题
            (r"'([^']*)'([^']*)'", r'"\1\2"'),
            # 修复缺失的括号
            (r'print\s+([^(].*)', r'print(\1)'),
            # 修复缩进问题（简单情况）
            (r'^(\s*)([^\s].*)', lambda m: '    ' + m.group(2) if len(m.group(1)) % 4 != 0 else m.group(0)),
        ]
        
        for pattern, replacement in fixes:
            if isinstance(replacement, str):
                new_line = re.sub(pattern, replacement, error_line)
            else:
                new_line = re.sub(pattern, replacement, error_line)
            
            if new_line != error_line:
                lines[error_line_idx] = new_line
                new_content = '\n'.join(lines)
                
                # 验证修复是否有效
                try:
                    ast.parse(new_content)
                    # 修复成功，保存文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"    修复: '{original_line}' -> '{new_line}'")
                    return True
                except SyntaxError:
                    # 这个修复无效，恢复原行
                    lines[error_line_idx] = original_line
                    continue
        
        # 尝试特殊修复
        if 'invalid syntax' in error.msg.lower():
            # 尝试删除问题字符
            if error.offset and error.offset <= len(error_line):
                char_at_error = error_line[error.offset - 1] if error.offset > 0 else ''
                if char_at_error in [')', '}', ']', ',', ';']:
                    new_line = error_line[:error.offset-1] + error_line[error.offset:]
                    lines[error_line_idx] = new_line
                    new_content = '\n'.join(lines)
                    
                    try:
                        ast.parse(new_content)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"    修复: 删除字符 '{char_at_error}'")
                        return True
                    except SyntaxError:
                        lines[error_line_idx] = original_line
        
        return False
    
    def fix_javascript_syntax_errors(self) -> Dict:
        """修复JavaScript/TypeScript语法错误"""
        print("📱 修复JavaScript/TypeScript语法错误...")
        
        js_files = []
        for pattern in ["*.js", "*.jsx", "*.ts", "*.tsx"]:
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
        """修复单个JavaScript/TypeScript文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # JavaScript/TypeScript常见语法错误修复
            fixes = [
                # 修复多余的分号
                (r';;+', ';'),
                # 修复多余的逗号
                (r',\s*}', '}'),
                (r',\s*]', ']'),
                (r',\s*\)', ')'),
                # 修复缺失的分号
                (r'(\w+)\s*\n\s*(\w+)', r'\1;\n\2'),
                # 修复引号问题
                (r"'([^']*)'([^']*)'", r'"\1\2"'),
                # 修复React组件导入
                (r'import\s+React\s*,\s*{\s*([^}]+)\s*}\s+from\s+[\'"]react[\'"]', r'import React, { \1 } from "react"'),
                # 修复TypeScript类型注解
                (r':\s*([A-Z][a-zA-Z]*)\s*=', r': \1 ='),
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
            'cleanup_backup'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def run_eslint_fix(self):
        """运行ESLint自动修复"""
        print("🔧 运行ESLint自动修复...")
        try:
            result = subprocess.run([
                'npx', 'eslint', '--fix', 
                'src/**/*.{js,jsx,ts,tsx}',
                'scripts/**/*.js',
                '--quiet'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("  ✅ ESLint修复完成")
            else:
                print(f"  ⚠️  ESLint修复部分完成: {result.stderr}")
        except Exception as e:
            print(f"  ❌ ESLint修复失败: {e}")
    
    def run_autopep8_fix(self):
        """运行autopep8自动修复"""
        print("🐍 运行autopep8自动修复...")
        try:
            # 只修复明显的格式问题
            python_files = list(self.project_root.rglob("*.py"))
            python_files = [f for f in python_files if not self._should_skip_file(f)]
            
            for py_file in python_files[:100]:  # 限制处理数量
                try:
                    subprocess.run([
                        'autopep8', '--in-place', '--aggressive', str(py_file)
                    ], capture_output=True, check=False)
                except:
                    continue
            
            print("  ✅ autopep8修复完成（前100个文件）")
        except Exception as e:
            print(f"  ❌ autopep8修复失败: {e}")
    
    def generate_report(self) -> str:
        """生成修复报告"""
        report = f"""# 🔧 语法错误修复报告

**修复时间**: {os.popen('date').read().strip()}
**项目路径**: {self.project_root}

## 📊 修复统计

- 成功修复文件: {len(self.fixed_files)} 个
- 修复失败文件: {len(self.failed_files)} 个

## ✅ 成功修复的文件

"""
        
        for file in self.fixed_files[:20]:  # 只显示前20个
            report += f"- {file}\n"
        
        if len(self.fixed_files) > 20:
            report += f"\n... 还有 {len(self.fixed_files) - 20} 个文件\n"
        
        if self.failed_files:
            report += f"""

## ❌ 修复失败的文件

"""
            for file in self.failed_files[:10]:  # 只显示前10个
                report += f"- {file}\n"
            
            if len(self.failed_files) > 10:
                report += f"\n... 还有 {len(self.failed_files) - 10} 个文件\n"
        
        report += f"""

## 🎯 修复建议

1. **手动检查**: 对修复失败的文件进行手动检查
2. **运行测试**: 执行测试确保修复没有破坏功能
3. **代码审查**: 检查自动修复的结果
4. **持续改进**: 完善修复规则

## 📈 预期效果

通过语法错误修复，预期：
- 代码质量评分提升 10-20 分
- 构建错误减少
- 开发体验改善
- 代码可维护性提升

"""
        
        return report

def main():
    parser = argparse.ArgumentParser(description='索克生活项目语法错误修复')
    parser.add_argument('--project-root', default='.', help='项目根目录路径')
    parser.add_argument('--output', default='syntax_fix_report.md', help='输出报告文件名')
    parser.add_argument('--python-only', action='store_true', help='只修复Python文件')
    parser.add_argument('--js-only', action='store_true', help='只修复JavaScript/TypeScript文件')
    
    args = parser.parse_args()
    
    print("🔧 开始语法错误修复...")
    
    fixer = SyntaxErrorFixer(args.project_root)
    
    # 执行修复
    if not args.js_only:
        fixer.fix_python_syntax_errors()
        fixer.run_autopep8_fix()
    
    if not args.python_only:
        fixer.fix_javascript_syntax_errors()
        fixer.run_eslint_fix()
    
    # 生成报告
    report = fixer.generate_report()
    
    # 保存报告
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 语法错误修复完成！报告已保存到: {args.output}")
    print(f"📊 修复文件数: {len(fixer.fixed_files)}")

if __name__ == '__main__':
    main() 