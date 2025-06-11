#!/usr/bin/env python3
"""
索克生活项目 - 项目代码语法错误修复工具
专门修复项目自身代码的语法错误，排除第三方库
"""

import os
import re
import ast
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SyntaxError:
    """语法错误信息"""
    file_path: str
    line_number: int
    column: int
    error_type: str
    message: str
    original_line: str
    fixed_line: Optional[str] = None

class ProjectSyntaxFixer:
    """项目语法错误修复器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.errors_found = []
        self.errors_fixed = []
        self.backup_dir = self.project_root / "backups" / "project_syntax_fixes"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 项目目录（只扫描这些目录）
        self.project_dirs = [
            "src",
            "services",
            "scripts",
            "tests",
            "examples"
        ]
        
        # 排除的目录模式
        self.exclude_patterns = [
            "*/.venv/*", "*/venv/*", "*/env/*",
            "*/node_modules/*", "*/.git/*", 
            "*/build/*", "*/dist/*", "*/__pycache__/*",
            "*/coverage/*", "*/htmlcov/*",
            "*/site-packages/*", "*/lib/python*/*",
            "*/Pods/*", "*/hermes-engine-artifacts/*",
            "*/xcuserdata/*", "*/xcshareddata/*"
        ]
        
        # 语法修复规则
        self.fix_patterns = [
            # 修复缺少冒号的问题
            (r'^(\s*)(def\s+\w+\s*\([^)]*\))\s*$', r'\1\2:'),
            (r'^(\s*)(class\s+\w+(?:\([^)]*\))?)\s*$', r'\1\2:'),
            (r'^(\s*)(if\s+.+[^:])\s*$', r'\1\2:'),
            (r'^(\s*)(elif\s+.+[^:])\s*$', r'\1\2:'),
            (r'^(\s*)(else)\s*$', r'\1\2:'),
            (r'^(\s*)(for\s+.+[^:])\s*$', r'\1\2:'),
            (r'^(\s*)(while\s+.+[^:])\s*$', r'\1\2:'),
            (r'^(\s*)(try)\s*$', r'\1\2:'),
            (r'^(\s*)(except(?:\s+\w+)?(?:\s+as\s+\w+)?)\s*$', r'\1\2:'),
            (r'^(\s*)(finally)\s*$', r'\1\2:'),
            (r'^(\s*)(with\s+.+[^:])\s*$', r'\1\2:'),
        ]
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """检查文件是否应该被排除"""
        file_str = str(file_path)
        
        for pattern in self.exclude_patterns:
            if file_path.match(pattern):
                return True
        
        # 检查是否在项目目录中
        relative_path = file_path.relative_to(self.project_root)
        first_part = str(relative_path).split('/')[0]
        
        if first_part not in self.project_dirs:
            return True
            
        return False
    
    def create_backup(self, file_path: Path) -> Path:
        """创建文件备份"""
        backup_path = self.backup_dir / file_path.relative_to(self.project_root)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_path.exists():
            backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
            logger.debug(f"创建备份: {backup_path}")
        
        return backup_path
    
    def check_syntax(self, file_path: Path) -> List[SyntaxError]:
        """检查文件语法错误"""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试编译代码
            try:
                ast.parse(content)
                return errors  # 没有语法错误
            except SyntaxError as e:
                error = SyntaxError(
                    file_path=str(file_path),
                    line_number=e.lineno or 0,
                    column=e.offset or 0,
                    error_type="SyntaxError",
                    message=str(e.msg),
                    original_line=e.text or ""
                )
                errors.append(error)
                
        except Exception as e:
            logger.error(f"检查文件 {file_path} 时出错: {e}")
        
        return errors
    
    def fix_missing_colons(self, content: str) -> str:
        """修复缺少的冒号"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            original_line = line
            
            # 跳过已经有冒号的行
            if line.rstrip().endswith(':'):
                fixed_lines.append(line)
                continue
            
            # 应用修复规则
            for pattern, replacement in self.fix_patterns:
                if re.match(pattern, line):
                    new_line = re.sub(pattern, replacement, line)
                    if new_line != line:
                        logger.info(f"修复冒号: '{line.strip()}' -> '{new_line.strip()}'")
                        line = new_line
                        break
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_indentation_errors(self, content: str) -> str:
        """修复缩进错误"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 移除行尾空白
            line = line.rstrip()
            
            # 检查是否有混合的制表符和空格
            if '\t' in line and ' ' in line:
                # 将制表符转换为4个空格
                line = line.expandtabs(4)
                logger.debug(f"修复制表符: {line[:20]}...")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_file(self, file_path: Path) -> bool:
        """修复单个文件的语法错误"""
        try:
            # 创建备份
            self.create_backup(file_path)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 应用各种修复
            content = original_content
            content = self.fix_indentation_errors(content)
            content = self.fix_missing_colons(content)
            
            # 如果内容有变化，写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # 验证修复结果
                errors_after = self.check_syntax(file_path)
                if not errors_after:
                    logger.info(f"✅ 成功修复: {file_path}")
                    return True
                else:
                    logger.warning(f"⚠️ 部分修复: {file_path} (仍有 {len(errors_after)} 个错误)")
                    # 显示剩余错误
                    for error in errors_after:
                        logger.warning(f"  行 {error.line_number}: {error.message}")
                    return False
            else:
                logger.debug(f"📄 无需修复: {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 修复文件 {file_path} 时出错: {e}")
            return False
    
    def scan_and_fix_project(self) -> Dict[str, int]:
        """扫描并修复整个项目"""
        stats = {
            'total_files': 0,
            'files_with_errors': 0,
            'files_fixed': 0,
            'files_failed': 0,
            'files_skipped': 0
        }
        
        # 扫描项目目录中的Python文件
        all_python_files = []
        for project_dir in self.project_dirs:
            dir_path = self.project_root / project_dir
            if dir_path.exists():
                all_python_files.extend(dir_path.rglob('*.py'))
        
        # 过滤文件
        filtered_files = []
        for file_path in all_python_files:
            if not self.should_exclude_file(file_path):
                filtered_files.append(file_path)
            else:
                stats['files_skipped'] += 1
        
        stats['total_files'] = len(filtered_files)
        logger.info(f"开始扫描 {stats['total_files']} 个项目Python文件...")
        logger.info(f"跳过 {stats['files_skipped']} 个第三方库文件")
        
        for file_path in filtered_files:
            try:
                # 检查语法错误
                errors = self.check_syntax(file_path)
                
                if errors:
                    stats['files_with_errors'] += 1
                    logger.info(f"🔍 发现语法错误: {file_path}")
                    for error in errors:
                        logger.info(f"  行 {error.line_number}: {error.message}")
                    
                    # 尝试修复
                    if self.fix_file(file_path):
                        stats['files_fixed'] += 1
                    else:
                        stats['files_failed'] += 1
                        
            except Exception as e:
                logger.error(f"处理文件 {file_path} 时出错: {e}")
                stats['files_failed'] += 1
        
        return stats
    
    def generate_report(self, stats: Dict[str, int]) -> str:
        """生成修复报告"""
        success_rate = (stats['files_fixed'] / max(stats['files_with_errors'], 1) * 100)
        
        report = f"""
# 索克生活项目 - 项目代码语法错误修复报告

## 📊 修复统计
- 扫描的项目文件: {stats['total_files']}
- 跳过的第三方库文件: {stats['files_skipped']}
- 有语法错误的文件: {stats['files_with_errors']}
- 成功修复的文件: {stats['files_fixed']}
- 修复失败的文件: {stats['files_failed']}

## 📈 修复成功率
- 成功率: {success_rate:.1f}%

## 🔧 修复内容
- 缺少冒号的语句（def, class, if, for, while等）
- 制表符和空格混用问题
- 行尾空白字符

## 📁 备份位置
所有修改的文件备份保存在: {self.backup_dir}

## 📂 扫描的项目目录
{', '.join(self.project_dirs)}

## ⚠️ 注意事项
1. 只修复了项目自身代码，未涉及第三方库
2. 请在修复后运行测试确保功能正常
3. 如有问题可从备份目录恢复原文件
4. 建议提交代码前再次检查语法

## 🚀 下一步建议
1. 运行项目测试: `python -m pytest tests/`
2. 检查代码质量: `flake8 src/ services/`
3. 格式化代码: `black src/ services/`
"""
        return report

def main():
    """主函数"""
    project_root = os.getcwd()
    
    print("🔧 索克生活项目 - 项目代码语法错误修复工具")
    print("=" * 60)
    
    fixer = ProjectSyntaxFixer(project_root)
    
    # 执行修复
    stats = fixer.scan_and_fix_project()
    
    # 生成报告
    report = fixer.generate_report(stats)
    
    # 保存报告
    report_file = Path(project_root) / "project_syntax_fix_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "=" * 60)
    print("📄 修复完成！详细报告已保存到 project_syntax_fix_report.md")
    print(f"📊 扫描文件: {stats['total_files']} 个")
    print(f"🔍 发现错误: {stats['files_with_errors']} 个文件")
    print(f"✅ 成功修复: {stats['files_fixed']} 个文件")
    print(f"❌ 修复失败: {stats['files_failed']} 个文件")
    
    if stats['files_with_errors'] == 0:
        print("\n🎉 恭喜！项目代码没有发现语法错误！")
        return 0
    elif stats['files_failed'] > 0:
        print(f"\n⚠️ {stats['files_failed']} 个文件修复失败，请手动检查")
        return 1
    else:
        print("\n🎉 所有语法错误已成功修复！")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 