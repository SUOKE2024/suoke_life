#!/usr/bin/env python3
"""
索克生活项目重复代码检测和重构脚本
检测并重构重复代码，提取公共函数和组件
"""

import os
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import difflib

class DuplicateCodeRefactor:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.duplicates_found = []
        self.refactored_files = []
        self.min_lines = 5  # 最少重复行数
        self.similarity_threshold = 0.8  # 相似度阈值
        
    def detect_and_refactor_duplicates(self) -> Dict:
        """检测并重构重复代码"""
        print("🔍 开始检测重复代码...")
        
        # 分别处理不同类型的文件
        python_result = self._process_python_files()
        typescript_result = self._process_typescript_files()
        
        # 合并结果
        total_result = {
            'python': python_result,
            'typescript': typescript_result,
            'total_duplicates_found': len(python_result['duplicates']) + len(typescript_result['duplicates']),
            'total_files_refactored': len(python_result['refactored_files']) + len(typescript_result['refactored_files'])
        }
        
        # 生成报告
        report = self._generate_report(total_result)
        total_result['report'] = report
        
        return total_result
    
    def _process_python_files(self) -> Dict:
        """处理Python文件的重复代码"""
        print("🐍 检测Python重复代码...")
        
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        
        # 提取代码块
        code_blocks = self._extract_python_code_blocks(python_files)
        
        # 检测重复
        duplicates = self._find_duplicates(code_blocks)
        
        # 重构重复代码
        refactored_files = self._refactor_python_duplicates(duplicates)
        
        return {
            'files_processed': len(python_files),
            'duplicates': duplicates,
            'refactored_files': refactored_files
        }
    
    def _process_typescript_files(self) -> Dict:
        """处理TypeScript文件的重复代码"""
        print("📘 检测TypeScript重复代码...")
        
        ts_files = []
        for pattern in ["*.ts", "*.tsx", "*.js", "*.jsx"]:
            ts_files.extend(self.project_root.rglob(pattern))
        
        ts_files = [f for f in ts_files if not self._should_skip_file(f)]
        
        # 提取代码块
        code_blocks = self._extract_typescript_code_blocks(ts_files)
        
        # 检测重复
        duplicates = self._find_duplicates(code_blocks)
        
        # 重构重复代码
        refactored_files = self._refactor_typescript_duplicates(duplicates)
        
        return {
            'files_processed': len(ts_files),
            'duplicates': duplicates,
            'refactored_files': refactored_files
        }
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = [
            'node_modules',
            '.git',
            'dist',
            'build',
            'coverage',
            '__pycache__',
            '.pytest_cache',
            'venv',
            'env',
            '.venv',
            'Pods',
            'android/app/build',
            'ios/build',
            '.test.',
            '.spec.',
            '__tests__'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def _extract_python_code_blocks(self, files: List[Path]) -> List[Dict]:
        """提取Python代码块"""
        code_blocks = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 提取函数和类
                current_block = []
                current_indent = 0
                block_start = 0
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    
                    # 检测函数或类定义
                    if (stripped.startswith('def ') or stripped.startswith('class ') or 
                        stripped.startswith('async def ')):
                        
                        # 保存之前的块
                        if len(current_block) >= self.min_lines:
                            code_blocks.append({
                                'file': file_path,
                                'start_line': block_start,
                                'end_line': i - 1,
                                'content': ''.join(current_block),
                                'hash': self._get_code_hash(''.join(current_block))
                            })
                        
                        # 开始新块
                        current_block = [line]
                        current_indent = len(line) - len(line.lstrip())
                        block_start = i
                    
                    elif current_block:
                        line_indent = len(line) - len(line.lstrip())
                        
                        # 如果缩进回到同级或更少，结束当前块
                        if stripped and line_indent <= current_indent:
                            if len(current_block) >= self.min_lines:
                                code_blocks.append({
                                    'file': file_path,
                                    'start_line': block_start,
                                    'end_line': i - 1,
                                    'content': ''.join(current_block),
                                    'hash': self._get_code_hash(''.join(current_block))
                                })
                            current_block = [line]
                            current_indent = line_indent
                            block_start = i
                        else:
                            current_block.append(line)
                
                # 处理最后一个块
                if len(current_block) >= self.min_lines:
                    code_blocks.append({
                        'file': file_path,
                        'start_line': block_start,
                        'end_line': len(lines) - 1,
                        'content': ''.join(current_block),
                        'hash': self._get_code_hash(''.join(current_block))
                    })
                    
            except Exception as e:
                print(f"❌ 处理文件失败 {file_path}: {e}")
        
        return code_blocks
    
    def _extract_typescript_code_blocks(self, files: List[Path]) -> List[Dict]:
        """提取TypeScript代码块"""
        code_blocks = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 使用正则表达式提取函数和组件
                patterns = [
                    r'(function\s+\w+\s*\([^)]*\)\s*\{[^}]*\})',
                    r'(const\s+\w+\s*=\s*\([^)]*\)\s*=>\s*\{[^}]*\})',
                    r'(export\s+function\s+\w+\s*\([^)]*\)\s*\{[^}]*\})',
                    r'(export\s+const\s+\w+\s*=\s*\([^)]*\)\s*=>\s*\{[^}]*\})'
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                    for match in matches:
                        block_content = match.group(1)
                        if len(block_content.split('\n')) >= self.min_lines:
                            code_blocks.append({
                                'file': file_path,
                                'start_pos': match.start(),
                                'end_pos': match.end(),
                                'content': block_content,
                                'hash': self._get_code_hash(block_content)
                            })
                            
            except Exception as e:
                print(f"❌ 处理文件失败 {file_path}: {e}")
        
        return code_blocks
    
    def _get_code_hash(self, content: str) -> str:
        """获取代码内容的哈希值"""
        # 标准化代码（移除空白和注释）
        normalized = re.sub(r'\s+', ' ', content)
        normalized = re.sub(r'//.*?\n', '', normalized)
        normalized = re.sub(r'/\*.*?\*/', '', normalized, flags=re.DOTALL)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _find_duplicates(self, code_blocks: List[Dict]) -> List[Dict]:
        """查找重复代码块"""
        duplicates = []
        hash_groups = defaultdict(list)
        
        # 按哈希值分组
        for block in code_blocks:
            hash_groups[block['hash']].append(block)
        
        # 找出重复的组
        for hash_value, blocks in hash_groups.items():
            if len(blocks) > 1:
                # 进一步检查相似度
                similar_groups = self._group_by_similarity(blocks)
                for group in similar_groups:
                    if len(group) > 1:
                        duplicates.append({
                            'hash': hash_value,
                            'blocks': group,
                            'count': len(group)
                        })
        
        return duplicates
    
    def _group_by_similarity(self, blocks: List[Dict]) -> List[List[Dict]]:
        """按相似度分组代码块"""
        groups = []
        
        for block in blocks:
            added_to_group = False
            
            for group in groups:
                # 检查与组中第一个块的相似度
                similarity = difflib.SequenceMatcher(
                    None, 
                    block['content'], 
                    group[0]['content']
                ).ratio()
                
                if similarity >= self.similarity_threshold:
                    group.append(block)
                    added_to_group = True
                    break
            
            if not added_to_group:
                groups.append([block])
        
        return groups
    
    def _refactor_python_duplicates(self, duplicates: List[Dict]) -> List[str]:
        """重构Python重复代码"""
        refactored_files = []
        
        for duplicate in duplicates[:5]:  # 限制处理数量
            try:
                # 创建公共函数
                common_function = self._create_python_common_function(duplicate)
                
                # 创建utils文件
                utils_file = self._create_python_utils_file(common_function)
                refactored_files.append(utils_file)
                
                print(f"✅ 已重构Python重复代码，创建公共函数: {utils_file}")
                
            except Exception as e:
                print(f"❌ Python重构失败: {e}")
        
        return refactored_files
    
    def _refactor_typescript_duplicates(self, duplicates: List[Dict]) -> List[str]:
        """重构TypeScript重复代码"""
        refactored_files = []
        
        for duplicate in duplicates[:5]:  # 限制处理数量
            try:
                # 创建公共函数
                common_function = self._create_typescript_common_function(duplicate)
                
                # 创建utils文件
                utils_file = self._create_typescript_utils_file(common_function)
                refactored_files.append(utils_file)
                
                print(f"✅ 已重构TypeScript重复代码，创建公共函数: {utils_file}")
                
            except Exception as e:
                print(f"❌ TypeScript重构失败: {e}")
        
        return refactored_files
    
    def _create_python_common_function(self, duplicate: Dict) -> str:
        """创建Python公共函数"""
        first_block = duplicate['blocks'][0]
        content = first_block['content']
        
        # 提取函数名
        match = re.search(r'def\s+(\w+)', content)
        func_name = match.group(1) if match else 'common_function'
        
        return f"""def {func_name}_common(*args, **kwargs):
    \"\"\"
    重构的公共函数，从重复代码中提取
    重复次数: {duplicate['count']}
    \"\"\"
{content}
"""
    
    def _create_typescript_common_function(self, duplicate: Dict) -> str:
        """创建TypeScript公共函数"""
        first_block = duplicate['blocks'][0]
        content = first_block['content']
        
        # 提取函数名
        match = re.search(r'(?:function\s+|const\s+)(\w+)', content)
        func_name = match.group(1) if match else 'commonFunction'
        
        return f"""/**
 * 重构的公共函数，从重复代码中提取
 * 重复次数: {duplicate['count']}
 */
export const {func_name}Common = {content};
"""
    
    def _create_python_utils_file(self, common_function: str) -> str:
        """创建Python utils文件"""
        utils_dir = self.project_root / 'src' / 'utils' / 'refactored'
        utils_dir.mkdir(parents=True, exist_ok=True)
        
        utils_file = utils_dir / 'common_functions.py'
        
        if utils_file.exists():
            with open(utils_file, 'a', encoding='utf-8') as f:
                f.write('\n\n' + common_function)
        else:
            with open(utils_file, 'w', encoding='utf-8') as f:
                f.write('"""重构的公共函数"""\n\n' + common_function)
        
        return str(utils_file)
    
    def _create_typescript_utils_file(self, common_function: str) -> str:
        """创建TypeScript utils文件"""
        utils_dir = self.project_root / 'src' / 'utils' / 'refactored'
        utils_dir.mkdir(parents=True, exist_ok=True)
        
        utils_file = utils_dir / 'commonFunctions.ts'
        
        if utils_file.exists():
            with open(utils_file, 'a', encoding='utf-8') as f:
                f.write('\n\n' + common_function)
        else:
            with open(utils_file, 'w', encoding='utf-8') as f:
                f.write('// 重构的公共函数\n\n' + common_function)
        
        return str(utils_file)
    
    def _generate_report(self, result: Dict) -> str:
        """生成重构报告"""
        report = f"""# 🔄 重复代码检测和重构报告

**重构时间**: {os.popen('date').read().strip()}
**项目路径**: {self.project_root}

## 📊 重构统计总览

- 总发现重复代码: {result['total_duplicates_found']} 组
- 总重构文件数: {result['total_files_refactored']}

### Python文件重构
- 处理文件数: {result['python']['files_processed']}
- 发现重复代码: {len(result['python']['duplicates'])} 组
- 重构文件数: {len(result['python']['refactored_files'])}

### TypeScript文件重构
- 处理文件数: {result['typescript']['files_processed']}
- 发现重复代码: {len(result['typescript']['duplicates'])} 组
- 重构文件数: {len(result['typescript']['refactored_files'])}

## 🔧 重构策略

### 重复代码检测
1. 最少重复行数: {self.min_lines}
2. 相似度阈值: {self.similarity_threshold}
3. 哈希算法: MD5
4. 相似度算法: SequenceMatcher

### 重构方法
1. 提取公共函数
2. 创建utils模块
3. 保持原有接口
4. 添加文档说明

## 📈 预期效果

通过重复代码重构，预期：
- 减少代码冗余
- 提升代码复用性
- 降低维护成本
- 提升代码质量评分
- 减少bug风险

## 🎯 建议

1. 定期运行重复代码检测
2. 在代码审查中关注重复代码
3. 建立代码复用规范
4. 使用设计模式减少重复
5. 建立公共组件库

## ⚠️ 注意事项

1. 重构后需要完整测试
2. 注意保持原有功能
3. 考虑性能影响
4. 更新相关文档
5. 通知团队成员

"""
        
        return report

def main():
    print("🔄 开始重复代码检测和重构...")
    
    refactor = DuplicateCodeRefactor('.')
    
    # 执行重构
    result = refactor.detect_and_refactor_duplicates()
    
    # 保存报告
    with open('duplicate_code_refactor_report.md', 'w', encoding='utf-8') as f:
        f.write(result['report'])
    
    print(f"✅ 重复代码重构完成！")
    print(f"📊 发现重复代码: {result['total_duplicates_found']} 组")
    print(f"📊 重构文件数: {result['total_files_refactored']}")
    print(f"📊 Python重复: {len(result['python']['duplicates'])} 组")
    print(f"📊 TypeScript重复: {len(result['typescript']['duplicates'])} 组")
    print(f"📄 报告已保存到: duplicate_code_refactor_report.md")

if __name__ == '__main__':
    main() 