"""
final_cleanup - 索克生活项目模块
"""

from pathlib import Path
import re

#!/usr/bin/env python3

"""
小艾服务最终清理脚本
处理剩余的关键代码质量问题
"""



class FinalCleanup:
    """最终清理器"""
    
    def __init__(self, base_path: str = "xiaoai"):
        self.base_path = Path(base_path)
        self.fixed_files = []
        
    def cleanup_all(self):
        """执行最终清理"""
        print("开始最终清理...")
        
        # 1. 移除所有注释代码
        self._remove_all_commented_code()
        
        # 2. 修复剩余的语法错误
        self._fix_remaining_syntax_errors()
        
        # 3. 修复全角标点符号
        self._fix_unicode_characters()
        
        # 4. 清理多余的pass语句
        self._cleanup_pass_statements()
        
        # 5. 修复导入问题
        self._fix_import_issues()
        
        print(f"最终清理完成！修复了 {len(self.fixed_files)} 个文件")
        
    def _remove_all_commented_code(self):
        """移除所有注释代码"""
        print("移除注释代码...")
        
        for py_file in self.base_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                # 移除明显的注释代码行
                lines = content.split('\n')
                cleaned_lines = []
                
                for line in lines:
                    stripped = line.strip()
                    
                    # 保留有意义的注释，移除注释的代码
                    if stripped.startswith('#'):
                        # 检查是否是代码注释
                        comment_content = stripped[1:].strip()
                        if (comment_content.startswith(('def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ', 'try:', 'except', 'return ', 'raise ')) or
                            comment_content.startswith(('{', '[', '"', "'")) or
                            comment_content.endswith(('}', ']', ')', ',', ';')) or
                            '=' in comment_content and not comment_content.startswith('=')):
                            continue  # 跳过注释的代码
                        else:
                            cleaned_lines.append(line)  # 保留有意义的注释
                    else:
                        cleaned_lines.append(line)
                
                content = '\n'.join(cleaned_lines)
                
                # 清理连续的空行
                content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
                
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    self.fixed_files.append(str(py_file))
                    
            except Exception as e:
                print(f"处理文件 {py_file} 时出错: {e}")
                
    def _fix_remaining_syntax_errors(self):
        """修复剩余的语法错误"""
        print("修复剩余语法错误...")
        
        for py_file in self.base_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                # 修复多语句在一行的问题
                content = re.sub(r'if\s+([^:]+):\s*([^:]+):\s*$', r'if \1:\n        \2', content, flags=re.MULTILINE)
                
                # 修复缩进问题
                lines = content.split('\n')
                fixed_lines = []
                
                for i, line in enumerate(lines):
                    # 修复错误的缩进
                    if line.strip().startswith('from ') and i > 0:
                        # 确保导入语句在正确位置
                        if not lines[i-1].strip().startswith(('from ', 'import ', '"""', "'''", '#')):
                            # 移动到文件顶部
                            continue
                    
                    fixed_lines.append(line)
                
                content = '\n'.join(fixed_lines)
                
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    self.fixed_files.append(str(py_file))
                    
            except Exception as e:
                print(f"处理文件 {py_file} 时出错: {e}")
                
    def _fix_unicode_characters(self):
        """修复全角标点符号"""
        print("修复全角标点符号...")
        
        # 全角到半角的映射
        punctuation_map = {
            '：': ':',
            '，': ',',
            '（': '(',
            '）': ')',
        }
        
        for py_file in self.base_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                # 只在注释中替换标点符号
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('#') or '"""' in line or "'''" in line:
                        for full_width, half_width in punctuation_map.items():
                            line = line.replace(full_width, half_width)
                        lines[i] = line
                
                content = '\n'.join(lines)
                
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    self.fixed_files.append(str(py_file))
                    
            except Exception as e:
                print(f"处理文件 {py_file} 时出错: {e}")
                
    def _cleanup_pass_statements(self):
        """清理多余的pass语句"""
        print("清理多余的pass语句...")
        
        for py_file in self.base_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                # 移除孤立的pass语句
                lines = content.split('\n')
                cleaned_lines = []
                
                for i, line in enumerate(lines):
                    if line.strip() == 'pass':
                        # 检查是否是必要的pass
                        if i > 0 and lines[i-1].strip().endswith(':'):
                            # 检查后面是否有其他语句
                            has_following_code = False
                            for j in range(i+1, len(lines)):
                                next_line = lines[j].strip()
                                if next_line and not next_line.startswith('#'):
                                    # 检查缩进级别
                                    if len(lines[j]) - len(lines[j].lstrip()) > len(line) - len(line.lstrip()):
                                        has_following_code = True
                                        break
                                    else:
                                        break
                            
                            if not has_following_code:
                                cleaned_lines.append(line)  # 保留必要的pass
                        # 否则跳过孤立的pass
                    else:
                        cleaned_lines.append(line)
                
                content = '\n'.join(cleaned_lines)
                
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    self.fixed_files.append(str(py_file))
                    
            except Exception as e:
                print(f"处理文件 {py_file} 时出错: {e}")
                
    def _fix_import_issues(self):
        """修复导入问题"""
        print("修复导入问题...")
        
        for py_file in self.base_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                # 修复typing导入
                content = re.sub(r'from typing import List', 'from typing import list', content)
                
                # 修复重复的导入
                lines = content.split('\n')
                seen_imports = set()
                cleaned_lines = []
                
                for line in lines:
                    if line.strip().startswith(('import ', 'from ')):
                        if line.strip() not in seen_imports:
                            seen_imports.add(line.strip())
                            cleaned_lines.append(line)
                    else:
                        cleaned_lines.append(line)
                
                content = '\n'.join(cleaned_lines)
                
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    self.fixed_files.append(str(py_file))
                    
            except Exception as e:
                print(f"处理文件 {py_file} 时出错: {e}")


def main():
    """主函数"""
    cleanup = FinalCleanup()
    cleanup.cleanup_all()
    
    print("\n修复的文件列表:")
    for file_path in set(cleanup.fixed_files):
        print(f"  - {file_path}")


if __name__ == "__main__":
    main()
