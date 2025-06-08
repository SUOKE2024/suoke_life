#!/usr/bin/env python3
"""
索克生活项目批量文件修复器
专门处理错误最多的文件，快速减少错误数量
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

class BatchFileFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.fixes_applied = []
        self.high_priority_files = [
            'src/screens/life/components/BlockchainHealthData.tsx',
            'src/screens/demo/ApiIntegrationDemo.tsx', 
            'src/components/blockchain/BlockchainDataManager.tsx',
            'src/agents/zkp_health_report.tsx',
            'src/agents/soer/SoerAgentImpl.ts',
            'src/screens/life/components/BlockchainHealthManager.tsx',
            'src/screens/demo/IntegrationDemoScreen.tsx',
            'src/screens/profile/ServiceManagementScreen.tsx',
            'src/screens/suoke/components/EcoLifestyleNavigator.tsx',
            'src/screens/life/HealthDashboardEnhanced.tsx'
        ]
        
    def execute_batch_fix(self):
        """执行批量文件修复"""
        print('🚀 启动批量文件修复器...')
        print('=' * 80)
        
        # 修复高优先级文件
        self._fix_high_priority_files()
        
        # 应用通用修复模式
        self._apply_universal_fixes()
        
        # 生成报告
        self._generate_report()
        
        print('\n🎉 批量文件修复完成！')
        
    def _fix_high_priority_files(self):
        """修复高优先级文件"""
        print('\n📋 修复高优先级文件...')
        print('-' * 50)
        
        for i, file_path in enumerate(self.high_priority_files, 1):
            print(f'🔧 [{i}/{len(self.high_priority_files)}] {file_path}')
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
            
            # 应用所有修复模式
            content, fixes_count = self._apply_all_fixes(content)
            
            if content != original_content:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                self.fixes_applied.append({
                    'file': file_path,
                    'fixes_count': fixes_count
                })
                
                print(f'  ✅ 修复 {fixes_count} 个问题')
            else:
                print(f'  ℹ️ 无需修复')
                
        except Exception as e:
            print(f'  ❌ 修复失败: {e}')
            
    def _apply_all_fixes(self, content: str) -> Tuple[str, int]:
        """应用所有修复模式"""
        fixes_count = 0
        
        # 1. 修复中文字符串引号问题
        patterns = [
            # 混合引号
            (r'"([^"]*[\u4e00-\u9fff][^"]*)\',\s*\'([^\']*)"', r'"\1", "\2"'),
            (r'\'([^\']*[\u4e00-\u9fff][^\']*)",\s*"([^"]*)\''', r'"\1", "\2"'),
            
            # 未终止的字符串
            (r'"([^"]*[\u4e00-\u9fff][^"]*),\s*([^"]*[\u4e00-\u9fff][^"]*)"', r'"\1", "\2"'),
            
            # 数组中的字符串
            (r'\["([^"]+)",([^"]+)\'\]', r'["\1", "\2"]'),
            (r'\[\'([^\']+)\',([^\']+)"\]', r'["\1", "\2"]'),
        ]
        
        for pattern, replacement in patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                fixes_count += len(matches)
                
        # 2. 修复函数定义语法
        function_patterns = [
            # 函数参数定义错误
            (r'(\w+)\(\)\n\s*([^)]+),\n\s*([^)]+),?\n\s*\): ([^{]+) \{', r'\1(\n  \2,\n  \3\n): \4 {'),
            (r'async (\w+)\(\)\n\s*([^)]+),\n\s*([^)]+),\n\s*([^)]+),\n\s*([^)]+),\n\s*([^)]+),\n\s*([^)]+),?\n\s*\): ([^{]+) \{', 
             r'async \1(\n  \2,\n  \3,\n  \4,\n  \5,\n  \6,\n  \7\n): \8 {'),
        ]
        
        for pattern, replacement in function_patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                fixes_count += len(matches)
                
        # 3. 修复对象和数组语法
        object_patterns = [
            # 对象属性后缺少逗号
            (r'(\w+): ([^,\n}]+)(\n\s*\w+:)', r'\1: \2,\3'),
            
            # 数组元素后缺少逗号
            (r'(["\'][\w\s\u4e00-\u9fff]+["\'])(\n\s*["\'])', r'\1,\2'),
            
            # 对象字面量语法错误
            (r'(\w+): \{,', r'\1: {'),
        ]
        
        for pattern, replacement in object_patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                fixes_count += len(matches)
                
        # 4. 修复JSX语法
        jsx_patterns = [
            # JSX标签语法错误
            (r'<(\w+);', r'<\1'),
            (r'<(\w+\.\w+);', r'<\1'),
            
            # JSX属性语法
            (r'style=\{ ([^}]+) \}', r'style={{ \1 }}'),
        ]
        
        for pattern, replacement in jsx_patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                fixes_count += len(matches)
                
        # 5. 修复React语法
        react_patterns = [
            # React.lazy语法
            (r'const (\w+) = React\.lazy\(\) => import\(', r'const \1 = React.lazy(() => import('),
            
            # useEffect语法
            (r'useEffect\(\) => \{', r'useEffect(() => {'),
            
            # 数组方法语法
            (r'\.filter\(\[([^]]+)\]\) =>', r'.filter([\1] =>'),
            (r'\.map\(\[([^]]+)\]\) => ([^)]+)\)', r'.map([\1] => \2)'),
            (r'\.reduce\(([^)]+)\) => ([^,]+), ([^)]+)\)', r'.reduce((\1) => \2, \3)'),
            (r'\.sort\(([^)]+), ([^)]+)\) => ([^)]+)\)', r'.sort((\1, \2) => \3)'),
        ]
        
        for pattern, replacement in react_patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                fixes_count += len(matches)
                
        # 6. 修复TypeScript语法
        ts_patterns = [
            # 类型定义错误
            (r'(\w+): ([^,]+),\n\s*([^)]+),?\n\s*\): ([^{]+) \{', r'\1: \2,\n  \3\n): \4 {'),
            
            # 接口定义错误
            (r'(\w+): ([^,]+),,', r'\1: \2,'),
        ]
        
        for pattern, replacement in ts_patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                fixes_count += len(matches)
                
        return content, fixes_count
        
    def _apply_universal_fixes(self):
        """应用通用修复模式"""
        print('\n📋 应用通用修复模式...')
        print('-' * 50)
        
        # 获取所有TypeScript/JavaScript文件
        all_files = []
        for ext in ['.ts', '.tsx', '.js', '.jsx']:
            files = list(self.project_root.rglob(f'src/**/*{ext}'))
            all_files.extend([str(f.relative_to(self.project_root)) for f in files])
            
        # 处理前50个文件
        for i, file_path in enumerate(all_files[:50], 1):
            if file_path not in self.high_priority_files:
                print(f'🔧 [{i}/50] {file_path}')
                self._fix_single_file(file_path)
                
    def _generate_report(self):
        """生成修复报告"""
        print('\n📊 生成批量修复报告...')
        
        total_files = len(self.fixes_applied)
        total_fixes = sum(fix['fixes_count'] for fix in self.fixes_applied)
        
        report_content = f"""# 批量文件修复报告

## 修复概览

**修复时间**: {self._get_current_time()}  
**修复文件数**: {total_files}  
**修复问题数**: {total_fixes}  
**修复类型**: 批量语法错误修复

---

## 高优先级文件修复

以下是错误最多的文件修复情况:

"""

        # 显示高优先级文件修复情况
        high_priority_fixes = [fix for fix in self.fixes_applied if fix['file'] in self.high_priority_files]
        for fix in high_priority_fixes:
            report_content += f"- ✅ {fix['file']}: {fix['fixes_count']} 个修复\n"
            
        report_content += f"""

## 修复模式统计

本次批量修复主要解决了以下问题:

1. **中文字符串引号问题**: 混合引号、未终止字符串
2. **函数定义语法错误**: 参数列表格式错误
3. **对象和数组语法**: 缺少逗号、括号不匹配
4. **JSX语法错误**: 标签语法、属性语法
5. **React语法错误**: lazy、useEffect、数组方法
6. **TypeScript语法**: 类型定义、接口定义

---

## 修复详情

"""

        for fix in self.fixes_applied:
            report_content += f"### {fix['file']} ({fix['fixes_count']} 个修复)\n\n"
            
        report_content += f"""

---

## 验证建议

1. **运行TypeScript检查**:
   ```bash
   npx tsc --noEmit
   ```

2. **启动开发服务器**:
   ```bash
   npm start
   ```

3. **运行测试**:
   ```bash
   npm test
   ```

---

**状态**: 批量文件修复完成  
**下一步**: 配置代码质量检查工具  
"""

        # 保存报告
        with open('BATCH_FILE_FIX_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        print(f'  ✅ 修复报告已生成: BATCH_FILE_FIX_REPORT.md')
        print(f'  📊 总计修复: {total_files}个文件, {total_fixes}个问题')
        
    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def main():
    """主函数"""
    fixer = BatchFileFixer()
    fixer.execute_batch_fix()

if __name__ == "__main__":
    main() 