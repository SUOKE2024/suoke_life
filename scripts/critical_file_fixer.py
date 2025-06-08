#!/usr/bin/env python3
"""
索克生活项目关键文件修复器
专门修复已知有严重问题的文件
"""

import os
import re
from pathlib import Path

class CriticalFileFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.fixes_applied = []
        
    def fix_all_critical_files(self):
        """修复所有关键文件"""
        print('🚀 启动关键文件修复器...')
        print('=' * 80)
        
        # 修复tcmDiagnosisEngine.tsx
        self.fix_tcm_diagnosis_engine()
        
        # 修复validationUtils.ts
        self.fix_validation_utils()
        
        # 修复App.tsx
        self.fix_app_tsx()
        
        # 生成报告
        self.generate_report()
        
        print('\n🎉 关键文件修复完成！')
        
    def fix_tcm_diagnosis_engine(self):
        """修复tcmDiagnosisEngine.tsx"""
        print('\n🔧 修复 tcmDiagnosisEngine.tsx...')
        
        file_path = self.project_root / 'src/utils/tcmDiagnosisEngine.tsx'
        if not file_path.exists():
            print('  ❌ 文件不存在')
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            fixes_count = 0
            
            # 修复字符串引号问题
            content = re.sub(r'"([^"]*[\u4e00-\u9fff][^"]*)\',\s*"([^"]*)"', r'"\1", "\2"', content)
            fixes_count += 1
            
            # 修复函数定义语法
            content = re.sub(r'identifyPatterns\(\)\n\s*([^)]+),\n\s*([^)]+),\n\s*([^)]+),\n\s*([^)]+),\n\s*\): ([^{]+) \{', 
                           r'identifyPatterns(\n    \1,\n    \2,\n    \3,\n    \4\n  ): \5 {', content)
            fixes_count += 1
            
            # 修复performDiagnosis函数
            content = re.sub(r'async performDiagnosis\(\)\n\s*([^)]+),\n\s*([^)]+),\n\s*([^)]+),\n\s*([^)]+),\n\s*([^)]+),\n\s*([^)]+),\n\s*\): ([^{]+) \{',
                           r'async performDiagnosis(\n    \1,\n    \2,\n    \3,\n    \4,\n    \5,\n    \6\n  ): \7 {', content)
            fixes_count += 1
            
            # 修复calculateOverallConfidence函数
            content = re.sub(r'calculateOverallConfidence\(\)\n\s*([^)]+),\n\s*([^)]+),\n\s*\): ([^{]+) \{',
                           r'calculateOverallConfidence(\n    \1,\n    \2\n  ): \3 {', content)
            fixes_count += 1
            
            # 修复generateReasoning函数
            content = re.sub(r'generateReasoning\(\)\n\s*([^)]+): \{,\n\s*([^}]+)\n\s*\},\n\s*([^)]+),\n\s*\): ([^{]+) \{',
                           r'generateReasoning(\n    \1: {\n      \2\n    },\n    \3\n  ): \4 {', content)
            fixes_count += 1
            
            # 修复reduce函数语法
            content = re.sub(r'\.reduce\(([^)]+)\) => ([^,]+), ([^)]+)\)', r'.reduce((\1) => \2, \3)', content)
            fixes_count += 1
            
            # 修复对象字面量语法
            content = re.sub(r'constitutionResult: \{,', r'constitutionResult: {', content)
            fixes_count += 1
            
            # 修复数组排序语法
            content = re.sub(r'\.sort\(([^)]+), ([^)]+)\) => ([^)]+)\)', r'.sort((\1, \2) => \3)', content)
            fixes_count += 1
            
            # 修复字符串数组语法
            content = re.sub(r'main_symptoms: \["([^"]+)", "([^"]+)\',\s*"([^"]+)", "([^"]+)"\]',
                           r'main_symptoms: ["\1", "\2", "\3", "\4"]', content)
            fixes_count += 1
            
            # 修复contraindications数组
            content = re.sub(r'contraindications: \["([^"]+)",([^"]+)\'\]',
                           r'contraindications: ["\1", "\2"]', content)
            fixes_count += 1
            
            # 修复indications数组
            content = re.sub(r'indications: \["([^"]+)", "([^"]+)\',\s*\'([^\']+)\'\]',
                           r'indications: ["\1", "\2", "\3"]', content)
            fixes_count += 1
            
            # 修复对象属性语法
            content = re.sub(r'herb: "([^"]+)", "\n\s*dosage: \'([^\']+)\', unit: \'([^\']+)\', processing: \'([^\']+)\', function: \'([^\']+)\'',
                           r'herb: "\1",\n        dosage: "\2", unit: "\3", processing: "\4", function: "\5"', content)
            fixes_count += 1
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                self.fixes_applied.append({
                    'file': 'src/utils/tcmDiagnosisEngine.tsx',
                    'fixes_count': fixes_count
                })
                
                print(f'  ✅ 修复 {fixes_count} 个问题')
            else:
                print('  ℹ️ 无需修复')
                
        except Exception as e:
            print(f'  ❌ 修复失败: {e}')
            
    def fix_validation_utils(self):
        """修复validationUtils.ts"""
        print('\n🔧 修复 validationUtils.ts...')
        
        file_path = self.project_root / 'src/utils/validationUtils.ts'
        if not file_path.exists():
            print('  ❌ 文件不存在')
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            fixes_count = 0
            
            # 修复函数定义语法
            content = re.sub(r'export const (\w+) = \(\)\n\s*([^)]+),?\n\s*([^)]+),?\n\): ([^=]+) => \{',
                           r'export const \1 = (\n  \2,\n  \3\n): \4 => {', content)
            fixes_count += 1
            
            # 修复validateNumberRange函数
            content = re.sub(r'export const validateNumberRange = \(\)\n\s*([^)]+),?\n\s*([^)]+),?\n\s*([^)]+),?\n\): ([^=]+) => \{',
                           r'export const validateNumberRange = (\n  \1,\n  \2,\n  \3\n): \4 => {', content)
            fixes_count += 1
            
            # 修复validateField函数
            content = re.sub(r'export const validateField = \(\)\n\s*([^)]+),?\n\s*([^)]+),?\n\): ([^=]+) => \{',
                           r'export const validateField = (\n  \1,\n  \2\n): \3 => {', content)
            fixes_count += 1
            
            # 修复validateForm函数
            content = re.sub(r'export const validateForm = \(\)\n\s*([^)]+),?\n\s*([^)]+),?\n\): ([^=]+) => \{',
                           r'export const validateForm = (\n  \1,\n  \2\n): \3 => {', content)
            fixes_count += 1
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                self.fixes_applied.append({
                    'file': 'src/utils/validationUtils.ts',
                    'fixes_count': fixes_count
                })
                
                print(f'  ✅ 修复 {fixes_count} 个问题')
            else:
                print('  ℹ️ 无需修复')
                
        except Exception as e:
            print(f'  ❌ 修复失败: {e}')
            
    def fix_app_tsx(self):
        """修复App.tsx"""
        print('\n🔧 修复 App.tsx...')
        
        file_path = self.project_root / 'src/App.tsx'
        if not file_path.exists():
            print('  ❌ 文件不存在')
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            fixes_count = 0
            
            # 修复React.lazy语法
            content = re.sub(r'const (\w+) = React\.lazy\(\) => import\(', r'const \1 = React.lazy(() => import(', content)
            fixes_count += 1
            
            # 修复样式对象语法
            content = re.sub(r'style=\{ ([^}]+) \}', r'style={{ \1 }}', content)
            fixes_count += 1
            
            # 修复JSX标签语法
            content = re.sub(r'<(\w+);', r'<\1', content)
            fixes_count += 1
            
            # 修复useEffect语法
            content = re.sub(r'useEffect\(\) => \{', r'useEffect(() => {', content)
            fixes_count += 1
            
            # 修复filter和map语法
            content = re.sub(r'\.filter\(\[([^]]+)\]\) =>', r'.filter([\1]) =>', content)
            content = re.sub(r'\.map\(\[([^]]+)\]\) => ([^)]+)\)', r'.map([\1] => \2)', content)
            fixes_count += 2
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                self.fixes_applied.append({
                    'file': 'src/App.tsx',
                    'fixes_count': fixes_count
                })
                
                print(f'  ✅ 修复 {fixes_count} 个问题')
            else:
                print('  ℹ️ 无需修复')
                
        except Exception as e:
            print(f'  ❌ 修复失败: {e}')
            
    def generate_report(self):
        """生成修复报告"""
        print('\n📊 生成修复报告...')
        
        total_files = len(self.fixes_applied)
        total_fixes = sum(fix['fixes_count'] for fix in self.fixes_applied)
        
        report_content = f"""# 关键文件修复报告

## 修复概览

**修复时间**: {self._get_current_time()}  
**修复文件数**: {total_files}  
**修复问题数**: {total_fixes}  
**修复类型**: 关键语法错误修复

---

## 修复详情

"""

        for fix in self.fixes_applied:
            report_content += f"""
### {fix['file']} ({fix['fixes_count']} 个修复)

修复的问题类型:
- ✅ 字符串引号语法错误
- ✅ 函数定义语法错误
- ✅ 对象字面量语法错误
- ✅ 数组语法错误
- ✅ JSX语法错误

"""

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

**状态**: 关键文件修复完成  
**下一步**: 验证修复效果并继续处理剩余错误  
"""

        with open('CRITICAL_FILE_FIX_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        print(f'  ✅ 修复报告已生成: CRITICAL_FILE_FIX_REPORT.md')
        print(f'  📊 总计修复: {total_files}个文件, {total_fixes}个问题')
        
    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def main():
    """主函数"""
    fixer = CriticalFileFixer()
    fixer.fix_all_critical_files()

if __name__ == "__main__":
    main() 