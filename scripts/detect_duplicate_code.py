#!/usr/bin/env python3
"""
重复代码检测工具
检测项目中的重复代码块，提供重构建议
"""

import ast
import difflib
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Set, Tuple


class CodeBlock:
    """代码块类"""

    def __init__(
        self,
        content: str,
        file_path: str,
        start_line: int,
        end_line: int,
        block_type: str = "function",
    ):
        self.content = content.strip()
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line
        self.block_type = block_type
        self.hash = self._calculate_hash()
        self.normalized_content = self._normalize_content()

    def _calculate_hash(self) -> str:
        """计算代码块哈希值"""
        return hashlib.md5(self.content.encode()).hexdigest()

    def _normalize_content(self) -> str:
        """标准化代码内容（移除空白、注释等）"""
        lines = []
        for line in self.content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                # 移除多余空格
                line = " ".join(line.split())
                lines.append(line)
        return "\n".join(lines)


class DuplicateCodeDetector:
    """重复代码检测器"""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.code_blocks: List[CodeBlock] = []
        self.duplicates: Dict[str, List[CodeBlock]] = defaultdict(list)
        self.similarity_threshold = 0.8
        self.min_lines = 5  # 最小行数阈值

    def scan_project(self) -> Dict[str, Any]:
        """扫描整个项目"""
        print("🔍 开始扫描项目中的重复代码...")

        stats = {
            "total_files": 0,
            "scanned_files": 0,
            "total_blocks": 0,
            "duplicate_groups": 0,
            "total_duplicates": 0,
            "potential_savings": 0,
        }

        # 扫描Python文件
        for root, dirs, files in os.walk(self.project_root):
            # 跳过特定目录
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d
                not in ["__pycache__", "node_modules", "venv", "env", "build", "dist"]
            ]

            for file in files:
                if file.endswith(".py"):
                    stats["total_files"] += 1
                    file_path = os.path.join(root, file)
                    try:
                        self._analyze_file(file_path)
                        stats["scanned_files"] += 1
                    except Exception as e:
                        print(f"⚠️  分析文件失败 {file_path}: {e}")

        # 检测重复代码
        self._detect_duplicates()

        # 更新统计信息
        stats["total_blocks"] = len(self.code_blocks)
        stats["duplicate_groups"] = len(self.duplicates)
        stats["total_duplicates"] = sum(
            len(blocks) for blocks in self.duplicates.values()
        )
        stats["potential_savings"] = self._calculate_potential_savings()

        return stats

    def _analyze_file(self, file_path: str):
        """分析单个文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 解析AST
            tree = ast.parse(content)

            # 提取函数和类
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self._extract_function_block(node, content, file_path)
                elif isinstance(node, ast.ClassDef):
                    self._extract_class_block(node, content, file_path)

        except Exception as e:
            # 如果AST解析失败，尝试简单的行分析
            self._analyze_file_by_lines(file_path)

    def _extract_function_block(
        self, node: ast.FunctionDef, content: str, file_path: str
    ):
        """提取函数代码块"""
        lines = content.split("\n")
        start_line = node.lineno
        end_line = node.end_lineno if hasattr(node, "end_lineno") else start_line + 10

        if end_line - start_line >= self.min_lines:
            block_content = "\n".join(lines[start_line - 1 : end_line])
            block = CodeBlock(
                block_content, file_path, start_line, end_line, "function"
            )
            self.code_blocks.append(block)

    def _extract_class_block(self, node: ast.ClassDef, content: str, file_path: str):
        """提取类代码块"""
        lines = content.split("\n")
        start_line = node.lineno
        end_line = node.end_lineno if hasattr(node, "end_lineno") else start_line + 20

        if end_line - start_line >= self.min_lines:
            block_content = "\n".join(lines[start_line - 1 : end_line])
            block = CodeBlock(block_content, file_path, start_line, end_line, "class")
            self.code_blocks.append(block)

    def _analyze_file_by_lines(self, file_path: str):
        """按行分析文件（AST解析失败时的备选方案）"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # 查找连续的代码块
            current_block = []
            start_line = 0

            for i, line in enumerate(lines):
                line = line.strip()
                if line and not line.startswith("#"):
                    if not current_block:
                        start_line = i + 1
                    current_block.append(line)
                else:
                    if len(current_block) >= self.min_lines:
                        block_content = "\n".join(current_block)
                        block = CodeBlock(
                            block_content, file_path, start_line, i, "block"
                        )
                        self.code_blocks.append(block)
                    current_block = []

            # 处理文件末尾的代码块
            if len(current_block) >= self.min_lines:
                block_content = "\n".join(current_block)
                block = CodeBlock(
                    block_content, file_path, start_line, len(lines), "block"
                )
                self.code_blocks.append(block)

        except Exception as e:
            print(f"⚠️  按行分析文件失败 {file_path}: {e}")

    def _detect_duplicates(self):
        """检测重复代码"""
        print("🔍 检测重复代码...")

        # 按哈希值分组
        hash_groups = defaultdict(list)
        for block in self.code_blocks:
            hash_groups[block.hash].append(block)

        # 找出重复的哈希组
        for hash_value, blocks in hash_groups.items():
            if len(blocks) > 1:
                self.duplicates[hash_value] = blocks

        # 检测相似代码（不完全相同但相似度高）
        self._detect_similar_code()

    def _detect_similar_code(self):
        """检测相似代码"""
        print("🔍 检测相似代码...")

        processed = set()

        for i, block1 in enumerate(self.code_blocks):
            if block1.hash in processed:
                continue

            similar_blocks = [block1]

            for j, block2 in enumerate(self.code_blocks[i + 1 :], i + 1):
                if block2.hash in processed:
                    continue

                similarity = self._calculate_similarity(
                    block1.normalized_content, block2.normalized_content
                )
                if similarity >= self.similarity_threshold:
                    similar_blocks.append(block2)

            if len(similar_blocks) > 1:
                # 使用第一个块的哈希作为组标识
                group_key = f"similar_{block1.hash}"
                self.duplicates[group_key] = similar_blocks
                for block in similar_blocks:
                    processed.add(block.hash)

    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """计算两个代码块的相似度"""
        if not content1 or not content2:
            return 0.0

        # 使用difflib计算相似度
        similarity = difflib.SequenceMatcher(None, content1, content2).ratio()
        return similarity

    def _calculate_potential_savings(self) -> int:
        """计算潜在的代码行数节省"""
        savings = 0
        for blocks in self.duplicates.values():
            if len(blocks) > 1:
                # 假设可以将重复代码重构为一个函数
                max_lines = max(block.end_line - block.start_line for block in blocks)
                savings += (len(blocks) - 1) * max_lines
        return savings

    def generate_report(self) -> Dict[str, Any]:
        """生成重复代码检测报告"""
        print("📊 生成重复代码检测报告...")

        report = {
            "scan_time": datetime.now().isoformat(),
            "summary": {
                "total_files": len(set(block.file_path for block in self.code_blocks)),
                "total_blocks": len(self.code_blocks),
                "duplicate_groups": len(self.duplicates),
                "total_duplicates": sum(
                    len(blocks) for blocks in self.duplicates.values()
                ),
                "potential_savings": self._calculate_potential_savings(),
            },
            "duplicate_groups": [],
            "recommendations": [],
        }

        # 按重复次数排序
        sorted_duplicates = sorted(
            self.duplicates.items(), key=lambda x: len(x[1]), reverse=True
        )

        for group_id, blocks in sorted_duplicates:
            group_info = {
                "group_id": group_id,
                "duplicate_count": len(blocks),
                "block_type": blocks[0].block_type,
                "lines_per_block": blocks[0].end_line - blocks[0].start_line,
                "total_duplicate_lines": sum(
                    block.end_line - block.start_line for block in blocks
                ),
                "locations": [],
            }

            for block in blocks:
                location = {
                    "file": os.path.relpath(block.file_path, self.project_root),
                    "start_line": block.start_line,
                    "end_line": block.end_line,
                    "preview": (
                        block.content[:200] + "..."
                        if len(block.content) > 200
                        else block.content
                    ),
                }
                group_info["locations"].append(location)

            report["duplicate_groups"].append(group_info)

        # 生成重构建议
        report["recommendations"] = self._generate_recommendations()

        return report

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """生成重构建议"""
        recommendations = []

        # 高优先级：大量重复的代码块
        high_priority = [
            (group_id, blocks)
            for group_id, blocks in self.duplicates.items()
            if len(blocks) >= 3 and (blocks[0].end_line - blocks[0].start_line) >= 10
        ]

        if high_priority:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "title": "提取公共函数",
                    "description": f"发现 {len(high_priority)} 组高度重复的代码块，建议提取为公共函数",
                    "action": "将重复代码提取为独立函数，并在原位置调用",
                    "estimated_savings": sum(
                        (len(blocks) - 1) * (blocks[0].end_line - blocks[0].start_line)
                        for _, blocks in high_priority
                    ),
                }
            )

        # 中优先级：中等重复的代码块
        medium_priority = [
            (group_id, blocks)
            for group_id, blocks in self.duplicates.items()
            if len(blocks) == 2 and (blocks[0].end_line - blocks[0].start_line) >= 5
        ]

        if medium_priority:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "title": "重构相似代码",
                    "description": f"发现 {len(medium_priority)} 组相似代码块，建议重构",
                    "action": "分析代码差异，提取公共部分，参数化差异部分",
                    "estimated_savings": sum(
                        (blocks[0].end_line - blocks[0].start_line) // 2
                        for _, blocks in medium_priority
                    ),
                }
            )

        # 低优先级：小的重复代码块
        low_priority = [
            (group_id, blocks)
            for group_id, blocks in self.duplicates.items()
            if len(blocks) >= 2 and (blocks[0].end_line - blocks[0].start_line) < 5
        ]

        if low_priority:
            recommendations.append(
                {
                    "priority": "LOW",
                    "title": "创建工具函数",
                    "description": f"发现 {len(low_priority)} 组小的重复代码片段",
                    "action": "考虑创建工具函数或常量来减少重复",
                    "estimated_savings": len(low_priority) * 2,
                }
            )

        return recommendations


def main():
    """主函数"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print("🚀 启动重复代码检测工具...")
    print(f"📁 项目根目录: {project_root}")

    detector = DuplicateCodeDetector(project_root)

    # 扫描项目
    stats = detector.scan_project()

    # 生成报告
    report = detector.generate_report()

    # 保存报告
    report_file = os.path.join(project_root, "duplicate_code_report.md")

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# 重复代码检测报告\n\n")
        f.write(f"**生成时间**: {report['scan_time']}\n\n")

        # 摘要
        f.write("## 📊 检测摘要\n\n")
        summary = report["summary"]
        f.write(f"- **扫描文件数**: {summary['total_files']}\n")
        f.write(f"- **代码块总数**: {summary['total_blocks']}\n")
        f.write(f"- **重复组数**: {summary['duplicate_groups']}\n")
        f.write(f"- **重复代码块数**: {summary['total_duplicates']}\n")
        f.write(f"- **潜在节省行数**: {summary['potential_savings']}\n\n")

        # 重复代码组
        if report["duplicate_groups"]:
            f.write("## 🔍 重复代码组\n\n")
            for i, group in enumerate(
                report["duplicate_groups"][:10], 1
            ):  # 只显示前10组
                f.write(f"### 组 {i}: {group['duplicate_count']} 个重复\n\n")
                f.write(f"- **类型**: {group['block_type']}\n")
                f.write(f"- **每块行数**: {group['lines_per_block']}\n")
                f.write(f"- **总重复行数**: {group['total_duplicate_lines']}\n\n")

                f.write("**位置**:\n")
                for location in group["locations"]:
                    f.write(
                        f"- `{location['file']}` (行 {location['start_line']}-{location['end_line']})\n"
                    )

                f.write(
                    f"\n**代码预览**:\n```python\n{group['locations'][0]['preview']}\n```\n\n"
                )

        # 重构建议
        if report["recommendations"]:
            f.write("## 💡 重构建议\n\n")
            for rec in report["recommendations"]:
                f.write(f"### {rec['priority']} 优先级: {rec['title']}\n\n")
                f.write(f"**描述**: {rec['description']}\n\n")
                f.write(f"**建议行动**: {rec['action']}\n\n")
                f.write(f"**预计节省行数**: {rec['estimated_savings']}\n\n")

    print(f"✅ 重复代码检测完成!")
    print(f"📄 报告已保存到: {report_file}")
    print(
        f"📊 发现 {summary['duplicate_groups']} 组重复代码，潜在节省 {summary['potential_savings']} 行代码"
    )

    return report


if __name__ == "__main__":
    main()
