#!/usr/bin/env python3
"""
ESLint错误修复器 - 专门修复导致ESLint解析失败的语法错误
"""

import os
import re
import sys
import subprocess
from pathlib import Path

class ESLintErrorFixer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.errors_found = []
        
    def fix_eslint_errors(self):
        """修复ESLint解析错误"""
        print("🔧 开始修复ESLint解析错误...")
        
        # 直接修复已知的问题文件
        problem_files = [
            'src/App.tsx',
            'src/setupTests.ts',
            'src/algorithms/config/AlgorithmConfig.tsx',
            'src/algorithms/modules/FiveDiagnosisSystem.ts',
            'src/config/AppConfig.ts',
            'src/config/onnxConfig.ts'
        ]
        
        for file_path in problem_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    self.fix_specific_file(full_path)
                except Exception as e:
                    self.errors_found.append(f"处理文件 {file_path} 时出错: {str(e)}")
        
        self.print_summary()
    
    def fix_specific_file(self, file_path: Path):
        """修复特定文件的语法错误"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 根据文件名应用特定修复
            if file_path.name == 'App.tsx':
                content = self.fix_app_tsx(content)
            elif file_path.name == 'setupTests.ts':
                content = self.fix_setup_tests(content)
            elif file_path.name == 'AlgorithmConfig.tsx':
                content = self.fix_algorithm_config(content)
            elif file_path.name == 'FiveDiagnosisSystem.ts':
                content = self.fix_five_diagnosis_system(content)
            elif file_path.name == 'AppConfig.ts':
                content = self.fix_app_config(content)
            elif file_path.name == 'onnxConfig.ts':
                content = self.fix_onnx_config(content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixed_files.append(str(file_path))
                print(f"✅ 修复文件: {file_path}")
                
        except Exception as e:
            self.errors_found.append(f"修复文件 {file_path} 时出错: {str(e)}")
    
    def fix_app_tsx(self, content: str) -> str:
        """修复App.tsx的语法错误"""
        # 修复条件渲染语法错误
        content = re.sub(r'&&\s*\)\s*\n\s*key\.startsWith', r'&& key.startsWith', content)
        
        # 修复Alert.alert语法
        content = re.sub(
            r'Alert\.alert\([^)]+\)\s*,\s*\n\s*\[\s*\n\s*\{[^}]+\}\s*,\s*\n\s*\{[^}]+\}\s*,\s*\n\s*\]\s*,\s*\n\s*\)',
            lambda m: m.group(0).replace('\n', ' ').replace('  ', ' '),
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        return content
    
    def fix_setup_tests(self, content: str) -> str:
        """修复setupTests.ts的语法错误"""
        # 修复导入语句中的语法错误
        content = re.sub(r'import\s+[^;]+;\s*\)\s*;', r'import "@testing-library/jest-native/extend-expect";', content)
        
        return content
    
    def fix_algorithm_config(self, content: str) -> str:
        """修复AlgorithmConfig.tsx的语法错误"""
        # 修复对象属性语法错误
        content = re.sub(r':\s*\{\s*\n\s*([^}]+)\s*\n\s*\}', r': {\n  \1\n}', content)
        
        return content
    
    def fix_five_diagnosis_system(self, content: str) -> str:
        """修复FiveDiagnosisSystem.ts的语法错误"""
        # 修复导入语句语法错误
        content = re.sub(r'import\s+[^;]+;\s*\)\s*;', r'import { DiagnosisResult } from "../types/diagnosis";', content)
        
        return content
    
    def fix_app_config(self, content: str) -> str:
        """修复AppConfig.ts的语法错误"""
        # 修复对象属性语法错误
        content = re.sub(r':\s*\{\s*\n\s*([^}]+)\s*\n\s*\}', r': {\n  \1\n}', content)
        
        return content
    
    def fix_onnx_config(self, content: str) -> str:
        """修复onnxConfig.ts的语法错误"""
        # 修复大括号匹配问题
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        if open_braces > close_braces:
            content += '\n' + '}' * (open_braces - close_braces)
        
        return content
    
    def print_summary(self):
        """打印修复总结"""
        print("\n" + "="*60)
        print("📊 ESLint错误修复总结")
        print("="*60)
        print(f"✅ 修复的文件数量: {len(self.fixed_files)}")
        print(f"❌ 错误数量: {len(self.errors_found)}")
        
        if self.fixed_files:
            print("\n📝 修复的文件:")
            for file_path in self.fixed_files:
                print(f"  - {file_path}")
        
        if self.errors_found:
            print("\n⚠️  错误信息:")
            for error in self.errors_found:
                print(f"  - {error}")

def main():
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    fixer = ESLintErrorFixer(project_root)
    fixer.fix_eslint_errors()

if __name__ == "__main__":
    main() 