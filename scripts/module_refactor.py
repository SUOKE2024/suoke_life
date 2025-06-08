#!/usr/bin/env python3
"""
索克生活项目模块重构器
解决设计层面的问题，重构问题模块
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

class ModuleRefactor:
    def __init__(self):
        self.project_root = Path.cwd()
        self.refactored_modules = []
        self.problem_modules = [
            'src/screens/life/components/BlockchainHealthData.tsx',
            'src/screens/demo/ApiIntegrationDemo.tsx',
            'src/components/blockchain/BlockchainDataManager.tsx',
            'src/agents/zkp_health_report.tsx',
            'src/agents/soer/SoerAgentImpl.ts'
        ]
        
    def execute_module_refactor(self):
        """执行模块重构"""
        print('🚀 启动模块重构器...')
        print('=' * 80)
        
        # 1. 分析问题模块
        self._analyze_problem_modules()
        
        # 2. 重构核心模块
        self._refactor_core_modules()
        
        # 3. 优化导入结构
        self._optimize_imports()
        
        # 4. 生成报告
        self._generate_report()
        
        print('\n🎉 模块重构完成！')
        
    def _analyze_problem_modules(self):
        """分析问题模块"""
        print('\n📋 分析问题模块...')
        print('-' * 50)
        
        for module_path in self.problem_modules:
            print(f'🔍 分析 {module_path}')
            self._analyze_single_module(module_path)
            
    def _analyze_single_module(self, module_path: str):
        """分析单个模块"""
        full_path = self.project_root / module_path
        
        if not full_path.exists():
            print(f'  ⚠️ 文件不存在')
            return
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 分析问题
            issues = []
            
            # 检查文件大小
            lines = content.split('\n')
            if len(lines) > 500:
                issues.append(f'文件过大 ({len(lines)} 行)')
                
            # 检查复杂度
            function_count = len(re.findall(r'function\s+\w+|const\s+\w+\s*=\s*\(', content))
            if function_count > 20:
                issues.append(f'函数过多 ({function_count} 个)')
                
            # 检查导入数量
            import_count = len(re.findall(r'^import\s+', content, re.MULTILINE))
            if import_count > 30:
                issues.append(f'导入过多 ({import_count} 个)')
                
            # 检查重复代码
            duplicate_patterns = self._find_duplicate_patterns(content)
            if duplicate_patterns:
                issues.append(f'重复代码模式 ({len(duplicate_patterns)} 个)')
                
            if issues:
                print(f'  ❌ 发现问题: {", ".join(issues)}')
            else:
                print(f'  ✅ 结构良好')
                
        except Exception as e:
            print(f'  ❌ 分析失败: {e}')
            
    def _find_duplicate_patterns(self, content: str) -> List[str]:
        """查找重复代码模式"""
        patterns = []
        
        # 查找重复的函数调用模式
        function_calls = re.findall(r'\w+\([^)]*\)', content)
        call_counts = {}
        for call in function_calls:
            call_counts[call] = call_counts.get(call, 0) + 1
            
        for call, count in call_counts.items():
            if count > 3 and len(call) > 20:
                patterns.append(call)
                
        return patterns
        
    def _refactor_core_modules(self):
        """重构核心模块"""
        print('\n📋 重构核心模块...')
        print('-' * 50)
        
        for module_path in self.problem_modules:
            print(f'🔧 重构 {module_path}')
            self._refactor_single_module(module_path)
            
    def _refactor_single_module(self, module_path: str):
        """重构单个模块"""
        full_path = self.project_root / module_path
        
        if not full_path.exists():
            print(f'  ⚠️ 文件不存在')
            return
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            refactor_count = 0
            
            # 应用重构模式
            content, count = self._apply_refactor_patterns(content)
            refactor_count += count
            
            if content != original_content:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                self.refactored_modules.append({
                    'module': module_path,
                    'refactor_count': refactor_count
                })
                
                print(f'  ✅ 重构 {refactor_count} 个问题')
            else:
                print(f'  ℹ️ 无需重构')
                
        except Exception as e:
            print(f'  ❌ 重构失败: {e}')
            
    def _apply_refactor_patterns(self, content: str) -> Tuple[str, int]:
        """应用重构模式"""
        refactor_count = 0
        
        # 1. 提取常量
        content, count = self._extract_constants(content)
        refactor_count += count
        
        # 2. 简化条件表达式
        content, count = self._simplify_conditions(content)
        refactor_count += count
        
        # 3. 优化函数结构
        content, count = self._optimize_functions(content)
        refactor_count += count
        
        # 4. 移除重复代码
        content, count = self._remove_duplicates(content)
        refactor_count += count
        
        return content, refactor_count
        
    def _extract_constants(self, content: str) -> Tuple[str, int]:
        """提取常量"""
        count = 0
        
        # 查找魔法数字和字符串
        magic_numbers = re.findall(r'\b\d{3,}\b', content)
        magic_strings = re.findall(r'"[^"]{20,}"', content)
        
        constants_section = "// Constants\n"
        
        # 提取数字常量
        for i, number in enumerate(set(magic_numbers)):
            if number.isdigit() and int(number) > 100:
                const_name = f"CONSTANT_{number}"
                constants_section += f"const {const_name} = {number};\n"
                content = content.replace(number, const_name, 1)
                count += 1
                
        # 提取字符串常量
        for i, string in enumerate(set(magic_strings)):
            if len(string) > 30:
                const_name = f"MESSAGE_{i + 1}"
                constants_section += f"const {const_name} = {string};\n"
                content = content.replace(string, const_name, 1)
                count += 1
                
        if count > 0:
            # 在文件开头添加常量
            import_end = content.find('\n\n')
            if import_end > 0:
                content = content[:import_end] + '\n\n' + constants_section + content[import_end:]
                
        return content, count
        
    def _simplify_conditions(self, content: str) -> Tuple[str, int]:
        """简化条件表达式"""
        count = 0
        
        # 简化复杂的条件表达式
        patterns = [
            # 简化 if (condition === true)
            (r'if\s*\(\s*(\w+)\s*===\s*true\s*\)', r'if (\1)'),
            
            # 简化 if (condition === false)
            (r'if\s*\(\s*(\w+)\s*===\s*false\s*\)', r'if (!\1)'),
            
            # 简化 condition ? true : false
            (r'(\w+)\s*\?\s*true\s*:\s*false', r'\1'),
            
            # 简化 condition ? false : true
            (r'(\w+)\s*\?\s*false\s*:\s*true', r'!\1'),
        ]
        
        for pattern, replacement in patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                count += len(matches)
                
        return content, count
        
    def _optimize_functions(self, content: str) -> Tuple[str, int]:
        """优化函数结构"""
        count = 0
        
        # 优化箭头函数
        patterns = [
            # 简化单行箭头函数
            (r'(\w+)\s*=\s*\([^)]*\)\s*=>\s*\{\s*return\s+([^;]+);\s*\}', r'\1 = (\2) => \2'),
            
            # 优化async函数
            (r'async\s+(\w+)\s*\([^)]*\)\s*\{\s*return\s+await\s+([^;]+);\s*\}', r'const \1 = async (\2) => await \2'),
        ]
        
        for pattern, replacement in patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                count += len(matches)
                
        return content, count
        
    def _remove_duplicates(self, content: str) -> Tuple[str, int]:
        """移除重复代码"""
        count = 0
        
        # 查找重复的代码块
        lines = content.split('\n')
        line_counts = {}
        
        for line in lines:
            stripped = line.strip()
            if len(stripped) > 20 and not stripped.startswith('//'):
                line_counts[stripped] = line_counts.get(stripped, 0) + 1
                
        # 移除重复行
        for line, line_count in line_counts.items():
            if line_count > 2:
                # 保留一个，移除其他
                occurrences = [i for i, l in enumerate(lines) if l.strip() == line]
                for i in reversed(occurrences[1:]):
                    lines.pop(i)
                    count += 1
                    
        content = '\n'.join(lines)
        return content, count
        
    def _optimize_imports(self):
        """优化导入结构"""
        print('\n📋 优化导入结构...')
        print('-' * 50)
        
        # 获取所有TypeScript文件
        ts_files = list(self.project_root.rglob('src/**/*.ts'))
        tsx_files = list(self.project_root.rglob('src/**/*.tsx'))
        
        all_files = ts_files + tsx_files
        
        for file_path in all_files[:20]:  # 处理前20个文件
            relative_path = file_path.relative_to(self.project_root)
            print(f'🔧 优化导入 {relative_path}')
            self._optimize_file_imports(file_path)
            
    def _optimize_file_imports(self, file_path: Path):
        """优化单个文件的导入"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # 优化导入顺序和结构
            content = self._reorganize_imports(content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'  ✅ 导入已优化')
            else:
                print(f'  ℹ️ 导入无需优化')
                
        except Exception as e:
            print(f'  ❌ 优化失败: {e}')
            
    def _reorganize_imports(self, content: str) -> str:
        """重新组织导入语句"""
        lines = content.split('\n')
        
        # 分离导入和其他代码
        imports = []
        other_lines = []
        in_imports = True
        
        for line in lines:
            if line.strip().startswith('import ') or line.strip().startswith('export '):
                if in_imports:
                    imports.append(line)
                else:
                    other_lines.append(line)
            elif line.strip() == '':
                if in_imports and imports:
                    imports.append(line)
                else:
                    other_lines.append(line)
            else:
                in_imports = False
                other_lines.append(line)
                
        # 对导入进行分组和排序
        react_imports = []
        library_imports = []
        local_imports = []
        
        for imp in imports:
            if 'react' in imp.lower():
                react_imports.append(imp)
            elif imp.strip().startswith('import ') and ('./' in imp or '../' in imp):
                local_imports.append(imp)
            elif imp.strip().startswith('import '):
                library_imports.append(imp)
                
        # 重新组织
        organized_imports = []
        if react_imports:
            organized_imports.extend(sorted(react_imports))
            organized_imports.append('')
            
        if library_imports:
            organized_imports.extend(sorted(library_imports))
            organized_imports.append('')
            
        if local_imports:
            organized_imports.extend(sorted(local_imports))
            organized_imports.append('')
            
        # 合并内容
        return '\n'.join(organized_imports + other_lines)
        
    def _generate_report(self):
        """生成重构报告"""
        print('\n📊 生成模块重构报告...')
        
        total_modules = len(self.refactored_modules)
        total_refactors = sum(module['refactor_count'] for module in self.refactored_modules)
        
        report_content = f"""# 模块重构报告

## 重构概览

**重构时间**: {self._get_current_time()}  
**重构模块数**: {total_modules}  
**重构操作数**: {total_refactors}  
**重构类型**: 常量提取、条件简化、函数优化、重复代码移除

---

## 重构详情

"""

        for module in self.refactored_modules:
            report_content += f"### {module['module']} ({module['refactor_count']} 个重构)\n\n"
            
        report_content += f"""

---

## 重构模式

本次模块重构主要应用了以下模式:

1. **常量提取**: 将魔法数字和长字符串提取为常量
2. **条件简化**: 简化复杂的条件表达式
3. **函数优化**: 优化箭头函数和async函数结构
4. **重复代码移除**: 移除重复的代码行
5. **导入优化**: 重新组织导入语句的顺序和结构

---

## 重构效果

### 代码质量改进
- **可读性**: 提取常量和简化条件提高了代码可读性
- **可维护性**: 移除重复代码降低了维护成本
- **一致性**: 统一的导入结构提高了代码一致性

### 性能优化
- **编译速度**: 优化的导入结构可能提高编译速度
- **运行时性能**: 简化的条件表达式可能提高运行时性能

---

## 验证建议

1. **运行测试**:
   ```bash
   npm test
   ```

2. **检查编译**:
   ```bash
   npx tsc --noEmit
   ```

3. **代码检查**:
   ```bash
   npm run lint
   ```

---

**状态**: 模块重构完成  
**下一步**: 建立长期监控系统  
"""

        # 保存报告
        with open('MODULE_REFACTOR_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        print(f'  ✅ 重构报告已生成: MODULE_REFACTOR_REPORT.md')
        print(f'  📊 总计重构: {total_modules}个模块, {total_refactors}个操作')
        
    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def main():
    """主函数"""
    refactor = ModuleRefactor()
    refactor.execute_module_refactor()

if __name__ == "__main__":
    main() 