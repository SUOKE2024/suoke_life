#!/usr/bin/env python3
"""
索克生活项目系统性Bug修复器
按照优先级分阶段修复所有发现的问题
"""

import os
import re
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict

class SystematicBugFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.fixes_applied = []
        self.error_patterns = self._load_error_patterns()
        
    def _load_error_patterns(self) -> Dict[str, Dict]:
        """加载常见错误模式和修复方案"""
        return {
            # React/JSX 语法错误
            'react_lazy_syntax': {
                'pattern': r'const (\w+) = React\.lazy\(\) => import\(',
                'replacement': r'const \1 = React.lazy(() => import(',
                'description': 'React.lazy语法错误'
            },
            'jsx_style_object': {
                'pattern': r'style=\{\s*([^}]+)\s*\}(?!\})',
                'replacement': r'style={{\1}}',
                'description': 'JSX样式对象语法错误'
            },
            'jsx_component_semicolon': {
                'pattern': r'<(\w+);',
                'replacement': r'<\1',
                'description': 'JSX组件分号错误'
            },
            'useEffect_syntax': {
                'pattern': r'useEffect\(\) => \{',
                'replacement': 'useEffect(() => {',
                'description': 'useEffect语法错误'
            },
            'reduce_callback_missing': {
                'pattern': r'\.reduce\(;',
                'replacement': '.reduce((acc, item) => acc + item, 0);',
                'description': 'reduce回调函数缺失'
            },
            'forEach_params': {
                'pattern': r'forEach\(([^)]+)\) =>',
                'replacement': r'forEach((\1) =>',
                'description': 'forEach参数语法错误'
            },
            'chinese_string_quotes': {
                'pattern': r'"([^"]*[\u4e00-\u9fff][^"]*)",([^"]*[\u4e00-\u9fff][^"]*)"',
                'replacement': r'"\1", "\2"',
                'description': '中文字符串引号错误'
            }
        }
        
    def execute_systematic_fix(self):
        """执行系统性修复"""
        print('🚀 启动系统性Bug修复器...')
        print('=' * 80)
        
        # 获取所有源码文件
        source_files = self._get_source_files()
        print(f'📊 发现 {len(source_files)} 个源码文件')
        
        # 修复所有文件
        self._fix_all_files(source_files)
        
        # 修复配置问题
        self._fix_configurations()
        
        # 生成报告
        self._generate_report()
        
        print('\n🎉 系统性Bug修复完成！')
        
    def _get_source_files(self) -> List[Path]:
        """获取所有源码文件"""
        patterns = ['src/**/*.ts', 'src/**/*.tsx', 'src/**/*.js', 'src/**/*.jsx']
        files = []
        for pattern in patterns:
            files.extend(self.project_root.glob(pattern))
        return files
        
    def _fix_all_files(self, files: List[Path]):
        """修复所有文件"""
        print('\n📋 修复源码文件...')
        print('-' * 50)
        
        for i, file_path in enumerate(files, 1):
            relative_path = file_path.relative_to(self.project_root)
            print(f'🔧 [{i}/{len(files)}] {relative_path}')
            self._fix_single_file(file_path, str(relative_path))
            
    def _fix_single_file(self, file_path: Path, relative_path: str):
        """修复单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            fixes_count = 0
            applied_fixes = []
            
            # 应用所有错误模式修复
            for pattern_name, pattern_info in self.error_patterns.items():
                pattern = pattern_info['pattern']
                replacement = pattern_info['replacement']
                description = pattern_info['description']
                
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    fixes_count += len(matches)
                    applied_fixes.append(f"{description} ({len(matches)}处)")
                    
            # 特殊修复
            content = self._fix_special_cases(content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                self.fixes_applied.append({
                    'file': relative_path,
                    'fixes_count': fixes_count,
                    'applied_fixes': applied_fixes
                })
                
                print(f'  ✅ 修复 {fixes_count} 个问题')
            else:
                print(f'  ℹ️ 无需修复')
                
        except Exception as e:
            print(f'  ❌ 修复失败: {e}')
            
    def _fix_special_cases(self, content: str) -> str:
        """修复特殊情况"""
        # 修复中文字符串问题
        content = re.sub(r'"([^"]*[\u4e00-\u9fff][^"]*)",([^"]*[\u4e00-\u9fff][^"]*)"', r'"\1", "\2"', content)
        
        # 修复缺少闭合括号
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 修复缺少闭合括号的问题
            open_parens = line.count('(')
            close_parens = line.count(')')
            
            if open_parens > close_parens and not line.strip().endswith('{'):
                missing_parens = open_parens - close_parens
                line = line.rstrip() + ')' * missing_parens
                
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def _fix_configurations(self):
        """修复配置问题"""
        print('\n📋 修复配置问题...')
        print('-' * 50)
        
        # 修复package.json
        self._fix_package_json()
        
    def _fix_package_json(self):
        """修复package.json"""
        print('🔧 修复package.json...')
        
        package_json_path = self.project_root / 'package.json'
        if not package_json_path.exists():
            print('  ❌ package.json不存在')
            return
            
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                
            # 移除问题依赖
            problematic_deps = [
                'react-native-sqlite-storage',
                '@types/react-native-sqlite-storage'
            ]
            
            removed_deps = []
            for dep in problematic_deps:
                if dep in package_data.get('dependencies', {}):
                    del package_data['dependencies'][dep]
                    removed_deps.append(dep)
                if dep in package_data.get('devDependencies', {}):
                    del package_data['devDependencies'][dep]
                    removed_deps.append(dep)
                    
            if removed_deps:
                with open(package_json_path, 'w', encoding='utf-8') as f:
                    json.dump(package_data, f, indent=2, ensure_ascii=False)
                print(f'  ✅ 移除问题依赖: {", ".join(removed_deps)}')
            else:
                print('  ℹ️ 无问题依赖需要移除')
                
        except Exception as e:
            print(f'  ❌ 修复package.json失败: {e}')
            
    def _generate_report(self):
        """生成修复报告"""
        print('\n📊 生成修复报告...')
        
        total_files = len(self.fixes_applied)
        total_fixes = sum(fix['fixes_count'] for fix in self.fixes_applied)
        
        report_content = f"""# 系统性Bug修复报告

## 修复概览

**修复时间**: {self._get_current_time()}  
**修复文件数**: {total_files}  
**修复问题数**: {total_fixes}  

---

## 修复详情

"""

        # 显示修复最多的前10个文件
        top_fixes = sorted(self.fixes_applied, key=lambda x: x['fixes_count'], reverse=True)[:10]
        
        for fix in top_fixes:
            report_content += f"""
### {fix['file']} ({fix['fixes_count']} 个修复)

修复内容:
"""
            for applied_fix in fix['applied_fixes']:
                report_content += f"- ✅ {applied_fix}\n"
                
        report_content += f"""

---

## 验证建议

运行以下命令验证修复效果:

```bash
# 检查TypeScript编译
npx tsc --noEmit

# 启动开发服务器
npm start
```

---

**状态**: 系统性修复完成，建议进行验证测试  
"""

        # 保存报告
        with open('SYSTEMATIC_BUG_FIX_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        print(f'  ✅ 修复报告已生成: SYSTEMATIC_BUG_FIX_REPORT.md')
        print(f'  📊 总计修复: {total_files}个文件, {total_fixes}个问题')
        
    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def main():
    """主函数"""
    fixer = SystematicBugFixer()
    fixer.execute_systematic_fix()

if __name__ == "__main__":
    main() 