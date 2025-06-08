#!/usr/bin/env python3
"""
精确语法修复器 - 修复特定的语法错误
"""

import os
import re
import sys
from pathlib import Path

class PreciseSyntaxFixer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.errors_found = []
        
    def fix_syntax_errors(self):
        """修复语法错误"""
        print("🔧 开始精确修复语法错误...")
        
        # 查找所有TypeScript和JavaScript文件
        patterns = ['**/*.tsx', '**/*.ts', '**/*.jsx', '**/*.js']
        files_to_check = []
        
        for pattern in patterns:
            files_to_check.extend(self.project_root.glob(pattern))
        
        # 过滤掉node_modules等目录
        files_to_check = [
            f for f in files_to_check 
            if not any(part in str(f) for part in ['node_modules', '.git', 'build', 'dist', 'coverage', 'venv', '.venv'])
        ]
        
        print(f"📁 找到 {len(files_to_check)} 个文件需要检查")
        
        for file_path in files_to_check:
            try:
                self.fix_file_syntax(file_path)
            except Exception as e:
                self.errors_found.append(f"处理文件 {file_path} 时出错: {str(e)}")
        
        self.print_summary()
    
    def fix_file_syntax(self, file_path: Path):
        """修复单个文件的语法错误"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 1. 修复条件渲染中的语法错误
            content = self.fix_conditional_rendering_syntax(content)
            
            # 2. 修复对象解构语法
            content = self.fix_object_destructuring_syntax(content)
            
            # 3. 修复Alert.alert语法
            content = self.fix_alert_syntax(content)
            
            # 4. 修复空的JSX注释
            content = self.fix_empty_jsx_comments(content)
            
            # 5. 修复函数参数语法
            content = self.fix_function_parameter_syntax(content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixed_files.append(str(file_path))
                print(f"✅ 修复文件: {file_path}")
                
        except Exception as e:
            self.errors_found.append(f"修复文件 {file_path} 时出错: {str(e)}")
    
    def fix_conditional_rendering_syntax(self, content: str) -> str:
        """修复条件渲染语法错误"""
        # 修复 {condition && <Component />} 中的语法错误
        # 修复 && ) 这种错误的语法
        content = re.sub(r'&&\s*\)\s*\n\s*key\.startsWith', r'&& key.startsWith', content)
        
        return content
    
    def fix_object_destructuring_syntax(self, content: str) -> str:
        """修复对象解构语法错误"""
        # 修复 filter((\[key, value\]) =>) 这种语法
        content = re.sub(r'filter\(\(\\\[([^\\]+)\\\]\)\s*=>', r'filter(([\\1]) =>', content)
        content = re.sub(r'map\(\(\\\[([^\\]+)\\\]\)\s*=>', r'map(([\\1]) =>', content)
        
        # 修复转义的方括号
        content = re.sub(r'\\\[([^\]]+)\\\]', r'[\1]', content)
        
        return content
    
    def fix_alert_syntax(self, content: str) -> str:
        """修复Alert.alert语法错误"""
        # 修复多行Alert.alert调用
        content = re.sub(
            r'Alert\.alert\(([\'"][^\'\"]*[\'"])\s*,\s*\n\s*([\'"][^\'\"]*[\'"])\s*,\s*\n\s*\[\s*\n\s*\{\s*\n\s*text:\s*([\'"][^\'\"]*[\'"])\s*,\s*\n\s*onPress:\s*([^}]+)\s*\}\s*,\s*\n\s*\{\s*\n\s*text:\s*([\'"][^\'\"]*[\'"])\s*,\s*\n\s*onPress:\s*([^}]+)\s*\}\s*,\s*\n\s*\]\s*,\s*\n\s*\)',
            r'Alert.alert(\1, \2, [{ text: \3, onPress: \4 }, { text: \5, onPress: \6 }])',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        return content
    
    def fix_empty_jsx_comments(self, content: str) -> str:
        """修复空的JSX注释"""
        # 移除空的JSX注释 {}
        content = re.sub(r'\s*\{\}\s*\n', r'\n', content)
        
        return content
    
    def fix_function_parameter_syntax(self, content: str) -> str:
        """修复函数参数语法错误"""
        # 修复函数参数中的语法错误
        content = re.sub(r'onPress:\s*([^}]+)\s*\}', r'onPress: \1 }', content)
        
        return content
    
    def print_summary(self):
        """打印修复总结"""
        print("\n" + "="*60)
        print("📊 精确语法修复总结")
        print("="*60)
        print(f"✅ 修复的文件数量: {len(self.fixed_files)}")
        print(f"❌ 错误数量: {len(self.errors_found)}")
        
        if self.fixed_files:
            print("\n📝 修复的文件:")
            for file_path in self.fixed_files[:10]:
                print(f"  - {file_path}")
            if len(self.fixed_files) > 10:
                print(f"  ... 还有 {len(self.fixed_files) - 10} 个文件")
        
        if self.errors_found:
            print("\n⚠️  错误信息:")
            for error in self.errors_found[:5]:
                print(f"  - {error}")
            if len(self.errors_found) > 5:
                print(f"  ... 还有 {len(self.errors_found) - 5} 个错误")

def main():
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    fixer = PreciseSyntaxFixer(project_root)
    fixer.fix_syntax_errors()

if __name__ == "__main__":
    main() 