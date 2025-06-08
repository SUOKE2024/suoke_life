#!/usr/bin/env python3
"""
索克生活项目中文字符串修复器
专门解决中文字符串引号混乱问题
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple

class ChineseStringFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.fixes_applied = []
        self.chinese_patterns = self._load_chinese_patterns()
        
    def _load_chinese_patterns(self) -> Dict[str, Dict]:
        """加载中文字符串修复模式"""
        return {
            # 混合引号问题
            'mixed_quotes_chinese': {
                'pattern': r'"([^"]*[\u4e00-\u9fff][^"]*)\',\s*\'([^\']*)"',
                'replacement': r'"\1", "\2"',
                'description': '修复中文字符串混合引号'
            },
            'mixed_quotes_reverse': {
                'pattern': r'\'([^\']*[\u4e00-\u9fff][^\']*)",\s*"([^"]*)\''',
                'replacement': r'"\1", "\2"',
                'description': '修复反向混合引号'
            },
            
            # 未终止的中文字符串
            'unterminated_chinese_string': {
                'pattern': r'"([^"]*[\u4e00-\u9fff][^"]*),\s*([^"]*[\u4e00-\u9fff][^"]*)"',
                'replacement': r'"\1", "\2"',
                'description': '修复未终止的中文字符串'
            },
            
            # 数组中的中文字符串
            'chinese_array_strings': {
                'pattern': r'\["([^"]*[\u4e00-\u9fff][^"]*)",\s*"([^"]*[\u4e00-\u9fff][^"]*)\',\s*\'([^\']*[\u4e00-\u9fff][^\']*)\'\]',
                'replacement': r'["\1", "\2", "\3"]',
                'description': '修复数组中的中文字符串'
            },
            
            # 对象属性中的中文字符串
            'chinese_object_values': {
                'pattern': r':\s*"([^"]*[\u4e00-\u9fff][^"]*)\',\s*\'([^\']*)"',
                'replacement': r': "\1", "\2"',
                'description': '修复对象属性中的中文字符串'
            },
            
            # 函数参数中的中文字符串
            'chinese_function_params': {
                'pattern': r'\("([^"]*[\u4e00-\u9fff][^"]*)\',\s*\'([^\']*[\u4e00-\u9fff][^\']*)"',
                'replacement': r'("\1", "\2"',
                'description': '修复函数参数中的中文字符串'
            },
            
            # 模板字符串中的中文
            'chinese_template_string': {
                'pattern': r'`([^`]*[\u4e00-\u9fff][^`]*)\$\{[^}]*;',
                'replacement': r'`\1${value}`;',
                'description': '修复模板字符串中的中文'
            },
            
            # JSX属性中的中文字符串
            'chinese_jsx_props': {
                'pattern': r'=\{"([^"]*[\u4e00-\u9fff][^"]*)\',\s*\'([^\']*)"',
                'replacement': r'={"\1"} \2="',
                'description': '修复JSX属性中的中文字符串'
            },
            
            # 注释中的引号问题
            'chinese_comments': {
                'pattern': r'//\s*([^"]*[\u4e00-\u9fff][^"]*)\',\s*\'([^\']*)',
                'replacement': r'// \1，\2',
                'description': '修复注释中的中文引号'
            }
        }
        
    def execute_chinese_string_fix(self):
        """执行中文字符串修复"""
        print('🚀 启动中文字符串修复器...')
        print('=' * 80)
        
        # 获取所有需要修复的文件
        target_files = self._get_target_files()
        print(f'📊 发现 {len(target_files)} 个需要检查的文件')
        
        # 修复所有文件
        self._fix_all_files(target_files)
        
        # 生成报告
        self._generate_report()
        
        print('\n🎉 中文字符串修复完成！')
        
    def _get_target_files(self) -> List[str]:
        """获取需要修复的文件列表"""
        target_extensions = ['.ts', '.tsx', '.js', '.jsx']
        target_files = []
        
        for ext in target_extensions:
            files = list(self.project_root.rglob(f'src/**/*{ext}'))
            target_files.extend([str(f.relative_to(self.project_root)) for f in files])
            
        return sorted(target_files)
        
    def _fix_all_files(self, target_files: List[str]):
        """修复所有文件"""
        print('\n📋 修复中文字符串问题...')
        print('-' * 50)
        
        for i, file_path in enumerate(target_files, 1):
            if i <= 100:  # 限制处理前100个文件
                print(f'🔧 [{i}/{min(len(target_files), 100)}] {file_path}')
                self._fix_single_file(file_path)
                
    def _fix_single_file(self, file_path: str):
        """修复单个文件"""
        full_path = self.project_root / file_path
        
        if not full_path.exists():
            print(f'  ⚠️ 文件不存在')
            return
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            fixes_count = 0
            applied_fixes = []
            
            # 应用所有中文字符串修复模式
            for pattern_name, pattern_info in self.chinese_patterns.items():
                pattern = pattern_info['pattern']
                replacement = pattern_info['replacement']
                description = pattern_info['description']
                
                matches = re.findall(pattern, content, re.MULTILINE)
                if matches:
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                    fixes_count += len(matches)
                    applied_fixes.append(f"{description} ({len(matches)}处)")
                    
            # 特殊修复逻辑
            content, special_fixes = self._apply_special_chinese_fixes(content)
            fixes_count += special_fixes
            
            if content != original_content:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                self.fixes_applied.append({
                    'file': file_path,
                    'fixes_count': fixes_count,
                    'applied_fixes': applied_fixes
                })
                
                print(f'  ✅ 修复 {fixes_count} 个中文字符串问题')
            else:
                print(f'  ℹ️ 无需修复')
                
        except Exception as e:
            print(f'  ❌ 修复失败: {e}')
            
    def _apply_special_chinese_fixes(self, content: str) -> Tuple[str, int]:
        """应用特殊的中文字符串修复"""
        fixes_count = 0
        
        # 修复常见的中文字符串模式
        patterns = [
            # 修复数组中的中文字符串
            (r'\["([^"]*[\u4e00-\u9fff][^"]*)",([^"]*[\u4e00-\u9fff][^"]*)\'\]', r'["\1", "\2"]'),
            
            # 修复对象中的中文字符串
            (r'(["\'][\u4e00-\u9fff][^"\']*),\s*(["\'][\u4e00-\u9fff][^"\']*["\'])', r'\1", \2'),
            
            # 修复函数调用中的中文字符串
            (r'\((["\'][\u4e00-\u9fff][^"\']*),\s*(["\'][\u4e00-\u9fff][^"\']*)\)', r'(\1, \2)'),
            
            # 修复JSX中的中文字符串
            (r'>([^<]*[\u4e00-\u9fff][^<]*),\s*([^<]*[\u4e00-\u9fff][^<]*)<', r'>\1，\2<'),
        ]
        
        for pattern, replacement in patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                fixes_count += len(matches)
                
        return content, fixes_count
        
    def _generate_report(self):
        """生成修复报告"""
        print('\n📊 生成中文字符串修复报告...')
        
        total_files = len(self.fixes_applied)
        total_fixes = sum(fix['fixes_count'] for fix in self.fixes_applied)
        
        report_content = f"""# 中文字符串修复报告

## 修复概览

**修复时间**: {self._get_current_time()}  
**修复文件数**: {total_files}  
**修复问题数**: {total_fixes}  
**修复类型**: 中文字符串引号和语法错误

---

## 修复详情

"""

        # 显示修复的文件
        for fix in self.fixes_applied:
            report_content += f"""
### {fix['file']} ({fix['fixes_count']} 个修复)

修复内容:
"""
            for applied_fix in fix['applied_fixes']:
                report_content += f"- ✅ {applied_fix}\n"
                
        report_content += f"""

---

## 修复模式统计

本次修复主要解决了以下中文字符串问题:

1. **混合引号问题**: 中文字符串使用了混合的单双引号
2. **未终止字符串**: 中文字符串没有正确闭合
3. **数组语法错误**: 数组中的中文字符串格式错误
4. **对象属性错误**: 对象属性值中的中文字符串问题
5. **函数参数错误**: 函数参数中的中文字符串格式问题
6. **JSX属性错误**: JSX组件属性中的中文字符串问题

---

## 验证建议

1. **运行TypeScript检查**:
   ```bash
   npx tsc --noEmit
   ```

2. **检查修复效果**:
   ```bash
   grep -r "[\u4e00-\u9fff].*'" src/ | head -10
   ```

3. **启动开发服务器**:
   ```bash
   npm start
   ```

---

**状态**: 中文字符串修复完成  
**下一步**: 继续执行批量文件修复  
"""

        # 保存报告
        with open('CHINESE_STRING_FIX_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        print(f'  ✅ 修复报告已生成: CHINESE_STRING_FIX_REPORT.md')
        print(f'  📊 总计修复: {total_files}个文件, {total_fixes}个中文字符串问题')
        
    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def main():
    """主函数"""
    fixer = ChineseStringFixer()
    fixer.execute_chinese_string_fix()

if __name__ == "__main__":
    main() 