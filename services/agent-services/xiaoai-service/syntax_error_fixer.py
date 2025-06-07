#!/usr/bin/env python3
"""
语法错误修复脚本 - 索克生活项目
专门修复重复类型注解和其他语法问题
"""

import re
from pathlib import Path


class SyntaxErrorFixer:
    """语法错误修复器"""
    
    def __init__(self, base_path: str = "xiaoai"):
        self.base_path = Path(base_path)
        self.fixed_files = []
        
    def fix_all_syntax_errors(self):
        """修复所有语法错误"""
        print("开始修复语法错误...")
        
        # 1. 修复重复类型注解
        self._fix_duplicate_type_annotations()
        
        # 2. 修复导入位置
        self._fix_import_positions()
        
        # 3. 修复其他语法问题
        self._fix_other_syntax_issues()
        
        # 4. 修复全局变量初始化
        self._fix_global_variable_initialization()
        
        print(f"语法错误修复完成！修复了 {len(self.fixed_files)} 个文件")
        
    def _fix_duplicate_type_annotations(self):
        """修复重复类型注解"""
        print("修复重复类型注解...")
        
        # 需要修复的文件和模式
        files_to_fix = [
            "four_diagnosis/enhanced_tongue_analysis.py",
            "observability/monitoring.py", 
            "service/enhanced_diagnosis_service.py",
            "service/xiaoai_service_impl.py",
            "utils/resilience.py"
        ]
        
        for file_path in files_to_fix:
            full_path = self.base_path / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')
                original_content = content
                
                # 修复重复类型注解模式: param: param: type -> param: type
                content = re.sub(
                    r'(\w+):\s*\1:\s*([^,\)]+)',
                    r'\1: \2',
                    content
                )
                
                # 修复特定的错误模式
                content = re.sub(
                    r'_image_data:\s*_image_data:\s*bytes',
                    r'_image_data: bytes',
                    content
                )
                
                content = re.sub(
                    r'_health_score:\s*_health_score:\s*int',
                    r'_health_score: int',
                    content
                )
                
                # 修复函数参数中的重复注解
                content = re.sub(
                    r'(\w+):\s*\1:\s*(dict\[str,\s*Any\])',
                    r'\1: \2',
                    content
                )
                
                content = re.sub(
                    r'(\w+):\s*\1:\s*(list\[str\])',
                    r'\1: \2',
                    content
                )
                
                content = re.sub(
                    r'(\w+):\s*\1:\s*str',
                    r'\1: str',
                    content
                )
                
                if content != original_content:
                    full_path.write_text(content, encoding='utf-8')
                    self.fixed_files.append(str(full_path))
                    
    def _fix_import_positions(self):
        """修复导入位置"""
        print("修复导入位置...")
        
        files_to_fix = [
            "four_diagnosis/tcm_algorithm.py",
            "service/cache_manager.py",
            "utils/config_loader.py",
            "utils/config_manager.py"
        ]
        
        for file_path in files_to_fix:
            full_path = self.base_path / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                # 分离导入和其他内容
                imports = []
                other_lines = []
                docstring_lines = []
                in_docstring = False
                docstring_started = False
                
                for line in lines:
                    stripped = line.strip()
                    
                    # 处理文档字符串
                    if not docstring_started and (stripped.startswith('"""') or stripped.startswith("'''")):
                        docstring_lines.append(line)
                        if stripped.count('"""') == 1 or stripped.count("'''") == 1:
                            in_docstring = True
                        docstring_started = True
                    elif in_docstring:
                        docstring_lines.append(line)
                        if stripped.endswith('"""') or stripped.endswith("'''"):
                            in_docstring = False
                    elif docstring_started and not in_docstring and (stripped.startswith('import ') or stripped.startswith('from ')):
                        imports.append(line)
                    elif docstring_started and not in_docstring:
                        other_lines.append(line)
                    else:
                        if not docstring_started:
                            docstring_lines.append(line)
                
                # 重新组织内容
                new_content = '\n'.join(docstring_lines + [''] + imports + [''] + other_lines)
                
                # 清理多余的空行
                new_content = re.sub(r'\n\s*\n\s*\n', '\n\n', new_content)
                
                if new_content != content:
                    full_path.write_text(new_content, encoding='utf-8')
                    self.fixed_files.append(str(full_path))
                    
    def _fix_other_syntax_issues(self):
        """修复其他语法问题"""
        print("修复其他语法问题...")
        
        for py_file in self.base_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                # 修复多语句在一行的问题
                content = re.sub(r':\s*(\w+):\s*$', r':', content, flags=re.MULTILINE)
                
                # 修复参数默认值问题
                content = re.sub(
                    r'jitter:\s*bool\s*=\s*True,\s*_max_backoff:\s*_max_backoff:\s*float\s*=\s*60\.0',
                    r'jitter: bool = True,\n    _max_backoff: float = 60.0',
                    content
                )
                
                # 修复函数定义中的语法错误
                content = re.sub(
                    r'def\s+(\w+)\s*\([^)]*\):\s*([^:]+):\s*$',
                    r'def \1(\2):',
                    content,
                    flags=re.MULTILINE
                )
                
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    self.fixed_files.append(str(py_file))
                    
            except Exception as e:
                print(f"处理文件 {py_file} 时出错: {e}")
                
    def _fix_global_variable_initialization(self):
        """修复全局变量初始化"""
        print("修复全局变量初始化...")
        
        # 需要添加全局变量初始化的文件
        global_vars = {
            "four_diagnosis/enhanced_tongue_analysis.py": "_tongue_analyzer = None",
            "four_diagnosis/knowledge_graph.py": "_knowledge_graph = None",
            "four_diagnosis/tcm_algorithm.py": "_tcm_algorithm = None",
            "service/cache_manager.py": "_cache_manager = None",
            "service/enhanced_diagnosis_service.py": "_diagnosis_service = None",
            "service/xiaoai_service_impl.py": "_xiaoai_service = None",
            "utils/config_loader.py": "_config_instance = None",
            "utils/config_manager.py": "_config_manager = None",
            "utils/metrics.py": "_metrics_collector = None"
        }
        
        for file_path, var_init in global_vars.items():
            full_path = self.base_path / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')
                
                # 检查是否已经有初始化
                var_name = var_init.split(' = ')[0]
                if f"{var_name} = None" not in content and f"{var_name}:" not in content:
                    # 找到合适的位置插入初始化
                    lines = content.split('\n')
                    insert_pos = 0
                    
                    # 找到导入语句后的位置
                    for i, line in enumerate(lines):
                        if line.strip().startswith('from ') or line.strip().startswith('import '):
                            insert_pos = i + 1
                        elif line.strip() == '' and insert_pos > 0:
                            insert_pos = i + 1
                            break
                    
                    # 插入全局变量初始化
                    lines.insert(insert_pos, f"\n# 全局变量初始化\n{var_init}\n")
                    
                    content = '\n'.join(lines)
                    full_path.write_text(content, encoding='utf-8')
                    self.fixed_files.append(str(full_path))


def main():
    """主函数"""
    fixer = SyntaxErrorFixer()
    fixer.fix_all_syntax_errors()
    
    print("\n修复的文件列表:")
    for file_path in set(fixer.fixed_files):
        print(f"  - {file_path}")


if __name__ == "__main__":
    main() 