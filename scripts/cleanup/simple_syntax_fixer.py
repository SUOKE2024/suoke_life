"""
simple_syntax_fixer - 索克生活项目模块
"""

from pathlib import Path
import os

#!/usr/bin/env python3
"""
索克生活项目简化语法错误修复脚本
专门处理测试文件的基本语法错误
"""


class SimpleSyntaxFixer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.failed_files = []
        
    def fix_test_files(self) -> dict:
        """修复测试文件的语法错误"""
        print("🔧 开始简化语法错误修复...")
        
        # 查找所有测试文件
        test_files = []
        for pattern in ["*.test.ts", "*.test.tsx", "*.spec.ts", "*.spec.tsx"]:
            test_files.extend(self.project_root.rglob(pattern))
        
        # 过滤掉不需要的文件
        test_files = [f for f in test_files if not self._should_skip_file(f)]
        
        print(f"找到 {len(test_files)} 个测试文件需要修复...")
        
        for file_path in test_files:
            try:
                if self._fix_single_file(file_path):
                    self.fixed_files.append(str(file_path))
                    print(f"  ✅ 已修复: {file_path}")
            except Exception as e:
                print(f"  ❌ 修复失败 {file_path}: {e}")
                self.failed_files.append(str(file_path))
        
        return {
            'fixed_files': len(self.fixed_files),
            'failed_files': len(self.failed_files),
            'total_files': len(test_files)
        }
    
    def _fix_single_file(self, file_path: Path) -> bool:
        """修复单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 应用修复策略
            content = self._fix_basic_syntax(content)
            
            # 如果内容有变化，保存文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
        except Exception as e:
            print(f"    修复错误: {e}")
            return False
        
        return False
    
    def _fix_basic_syntax(self, content: str) -> str:
        """修复基本语法错误"""
        # 分行处理
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 修复特定的语法错误
            fixed_line = self._fix_line_syntax(line)
            fixed_lines.append(fixed_line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_line_syntax(self, line: str) -> str:
        """修复单行语法错误"""
        # 修复it函数语法错误
        if 'it("should handle large datasets efficiently, () => { {' in line:
            return '  it("should handle large datasets efficiently", () => {'
        elif 'it("should not cause memory leaks\', () => { {' in line:
            return '  it("should not cause memory leaks", () => {'
        
        # 修复缺失分号的行
        if line.strip().endswith('});') and not line.strip().endswith('});'):
            # 检查前一行是否需要分号
            pass
        
        # 修复expect语句缺失分号
        if 'expect(' in line and line.strip().endswith(')') and not line.strip().endswith(');'):
            if '.toBeLessThan(' in line or '.toBe(' in line or '.toEqual(' in line:
                return line.rstrip() + ';'
        
        # 修复const声明缺失分号
        if line.strip().startswith('const ') and '=' in line and not line.strip().endswith(';'):
            return line.rstrip() + ';'
        
        # 修复函数调用缺失分号
        if 'performance.now()' in line and not line.strip().endswith(';'):
            return line.rstrip() + ';'
        elif 'global.gc()' in line and not line.strip().endswith(';'):
            return line.rstrip() + ';'
        elif 'someFunction(' in line and not line.strip().endswith(';'):
            return line.rstrip() + ';'
        
        # 修复process.memoryUsage()调用
        if 'process.memoryUsage().heapUsed' in line and not line.strip().endswith(';'):
            return line.rstrip() + ';'
        
        return line
    
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
        report = f"""# 🔧 简化语法错误修复报告

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

## 🔧 修复的问题类型

1. **it函数语法错误**
   - 修复it函数定义中的语法错误
   - 修复字符串引号问题
   - 修复多余的大括号

2. **缺失分号**
   - 修复expect语句缺失分号
   - 修复const声明缺失分号
   - 修复函数调用缺失分号

3. **函数调用语法**
   - 修复performance.now()调用
   - 修复global.gc()调用
   - 修复someFunction调用

4. **变量声明**
   - 修复process.memoryUsage()调用
   - 修复变量赋值语法

## 📈 预期效果

通过简化语法错误修复，预期：
- 基本的测试文件语法错误得到修复
- 减少语法错误数量
- 提高代码质量评分

"""
        
        return report

def main():
    print("🔧 开始简化语法错误修复...")
    
    fixer = SimpleSyntaxFixer('.')
    
    # 执行修复
    result = fixer.fix_test_files()
    
    # 生成报告
    report = fixer.generate_report()
    
    # 保存报告
    with open('simple_syntax_fix_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 简化语法错误修复完成！")
    print(f"📊 修复文件数: {result['fixed_files']}")
    print(f"❌ 失败文件数: {result['failed_files']}")
    print(f"📄 报告已保存到: simple_syntax_fix_report.md")

if __name__ == '__main__':
    main() 