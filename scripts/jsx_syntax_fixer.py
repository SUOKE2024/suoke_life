#!/usr/bin/env python3
"""
JSX语法修复器 - 专门修复React Native项目中的JSX语法错误
"""

import os
import re
import sys
from pathlib import Path

class JSXSyntaxFixer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.errors_found = []
        
    def fix_jsx_syntax_errors(self):
        """修复JSX语法错误"""
        print("🔧 开始修复JSX语法错误...")
        
        # 查找所有TypeScript和JavaScript文件
        patterns = ['**/*.tsx', '**/*.ts', '**/*.jsx', '**/*.js']
        files_to_check = []
        
        for pattern in patterns:
            files_to_check.extend(self.project_root.glob(pattern))
        
        # 过滤掉node_modules等目录
        files_to_check = [
            f for f in files_to_check 
            if not any(part in str(f) for part in ['node_modules', '.git', 'build', 'dist', 'coverage'])
        ]
        
        print(f"📁 找到 {len(files_to_check)} 个文件需要检查")
        
        for file_path in files_to_check:
            try:
                self.fix_file_jsx_syntax(file_path)
            except Exception as e:
                self.errors_found.append(f"处理文件 {file_path} 时出错: {str(e)}")
        
        self.print_summary()
    
    def fix_file_jsx_syntax(self, file_path: Path):
        """修复单个文件的JSX语法错误"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 1. 修复缺少return的JSX函数
            content = self.fix_missing_return_statements(content)
            
            # 2. 修复JSX属性语法错误
            content = self.fix_jsx_attribute_syntax(content)
            
            # 3. 修复条件渲染语法
            content = self.fix_conditional_rendering(content)
            
            # 4. 修复Alert.alert语法
            content = self.fix_alert_syntax(content)
            
            # 5. 修复对象解构语法
            content = self.fix_object_destructuring(content)
            
            # 6. 修复数组语法错误
            content = self.fix_array_syntax(content)
            
            # 7. 修复字符串模板语法
            content = self.fix_template_string_syntax(content)
            
            # 8. 修复括号匹配问题
            content = self.fix_bracket_matching(content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixed_files.append(str(file_path))
                print(f"✅ 修复文件: {file_path}")
                
        except Exception as e:
            self.errors_found.append(f"修复文件 {file_path} 时出错: {str(e)}")
    
    def fix_missing_return_statements(self, content: str) -> str:
        """修复缺少return语句的JSX函数"""
        # 修复 = () => () 后面跟JSX的情况
        content = re.sub(r'= \(\) => \(\)\s*\n\s*(<)', r'= () => (\n  \1', content)
        
        # 修复 return () 后面跟JSX的情况
        content = re.sub(r'return \(\)\s*\n\s*(<)', r'return (\n  \1', content)
        
        return content
    
    def fix_jsx_attribute_syntax(self, content: str) -> str:
        """修复JSX属性语法错误"""
        # 修复 style={{styles.xxx}} 应该是 style={styles.xxx}
        content = re.sub(r'style=\{\{(styles\.\w+)\}\}', r'style={\1}', content)
        
        # 修复 style={{[styles.xxx, ...]}} 应该是 style={[styles.xxx, ...]}
        content = re.sub(r'style=\{\{(\[styles\.[^\]]+\])\}\}', r'style={\1}', content)
        
        return content
    
    def fix_conditional_rendering(self, content: str) -> str:
        """修复条件渲染语法"""
        # 修复 {condition && () <Component />} 应该是 {condition && <Component />}
        content = re.sub(r'\{\s*([^}]+)\s*&&\s*\(\)\s*\n\s*(<)', r'{\1 && \2', content)
        
        return content
    
    def fix_alert_syntax(self, content: str) -> str:
        """修复Alert.alert语法错误"""
        # 修复 Alert.alert() 后面跟参数的情况
        content = re.sub(r'Alert\.alert\(\)\s*\n\s*([\'"][^\'\"]*[\'"])', r'Alert.alert(\1', content)
        
        return content
    
    def fix_object_destructuring(self, content: str) -> str:
        """修复对象解构语法错误"""
        # 修复转义的方括号
        content = re.sub(r'\\\[([^\]]+)\\\]', r'[\1]', content)
        
        return content
    
    def fix_array_syntax(self, content: str) -> str:
        """修复数组语法错误"""
        # 修复数组解构中的转义字符
        content = re.sub(r'\\\[([^\]]+)\\\]', r'[\1]', content)
        
        return content
    
    def fix_template_string_syntax(self, content: str) -> str:
        """修复模板字符串语法"""
        # 这里可以添加模板字符串相关的修复
        return content
    
    def fix_bracket_matching(self, content: str) -> str:
        """修复括号匹配问题"""
        # 修复Alert.alert()缺少参数的问题
        content = re.sub(r'Alert\.alert\(\)\s*\n\s*([\'"][^\'\"]+[\'"])', r'Alert.alert(\1', content)
        
        return content
    
    def print_summary(self):
        """打印修复总结"""
        print("\n" + "="*60)
        print("📊 JSX语法修复总结")
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
    
    fixer = JSXSyntaxFixer(project_root)
    fixer.fix_jsx_syntax_errors()

if __name__ == "__main__":
    main() 