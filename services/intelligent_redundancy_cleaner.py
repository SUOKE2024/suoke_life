#!/usr/bin/env python3
"""
索克生活 - 智能冗余文件清理器
基于services现有代码结构及具体实现，洞察冗余文件并清理

功能：
1. 识别备份文件 (.backup, .backup_advanced, .backup_priority)
2. 识别空占位符文件
3. 识别重复的配置文件
4. 识别未使用的临时文件
5. 生成清理报告
"""

import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple


class IntelligentRedundancyCleaner:
    """智能冗余文件清理器"""

    def __init__(self, services_root: str = "services"):
        self.services_root = Path(services_root)
        self.redundant_files = {
            "backup_files": [],
            "placeholder_files": [],
            "duplicate_files": [],
            "empty_files": [],
            "temp_files": [],
            "cache_files": [],
        }
        self.file_hashes = {}
        self.cleanup_stats = {
            "total_files_scanned": 0,
            "total_size_saved": 0,
            "files_removed": 0,
        }

    def scan_services(self) -> Dict:
        """扫描services目录识别冗余文件"""
        print("🔍 开始扫描services目录...")

        for root, dirs, files in os.walk(self.services_root):
            # 跳过虚拟环境和缓存目录
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(
                    (
                        ".venv",
                        "__pycache__",
                        ".pytest_cache",
                        ".mypy_cache",
                        ".ruff_cache",
                        "htmlcov",
                        ".benchmarks",
                    )
                )
            ]

            for file in files:
                file_path = Path(root) / file
                self.cleanup_stats["total_files_scanned"] += 1

                # 检查备份文件
                if self._is_backup_file(file):
                    self.redundant_files["backup_files"].append(str(file_path))

                # 检查占位符文件
                elif self._is_placeholder_file(file_path):
                    self.redundant_files["placeholder_files"].append(str(file_path))

                # 检查空文件
                elif self._is_empty_file(file_path):
                    self.redundant_files["empty_files"].append(str(file_path))

                # 检查临时文件
                elif self._is_temp_file(file):
                    self.redundant_files["temp_files"].append(str(file_path))

                # 检查缓存文件
                elif self._is_cache_file(file):
                    self.redundant_files["cache_files"].append(str(file_path))

                # 计算文件哈希用于重复检测
                else:
                    self._calculate_file_hash(file_path)

        # 识别重复文件
        self._find_duplicate_files()

        return self.redundant_files

    def _is_backup_file(self, filename: str) -> bool:
        """检查是否为备份文件"""
        backup_patterns = [
            ".backup",
            ".backup_advanced",
            ".backup_priority",
            ".bak",
            ".orig",
            ".old",
            ".tmp",
        ]
        return any(filename.endswith(pattern) for pattern in backup_patterns)

    def _is_placeholder_file(self, file_path: Path) -> bool:
        """检查是否为占位符文件"""
        try:
            if file_path.stat().st_size > 1000:  # 大于1KB的文件不太可能是占位符
                return False

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()

            # 检查常见的占位符模式
            placeholder_patterns = [
                '"""Module placeholder"""',
                'def main():\n    """Main function placeholder"""',
                "pass",
                "# TODO",
                "# PLACEHOLDER",
            ]

            return (
                any(pattern in content for pattern in placeholder_patterns)
                and len(content) < 200
            )

        except Exception:
            return False

    def _is_empty_file(self, file_path: Path) -> bool:
        """检查是否为空文件"""
        try:
            return file_path.stat().st_size == 0
        except Exception:
            return False

    def _is_temp_file(self, filename: str) -> bool:
        """检查是否为临时文件"""
        temp_patterns = [
            ".tmp",
            ".temp",
            ".swp",
            ".swo",
            "~",
            "fix_",
            "test_quick",
            "demo_",
        ]
        return any(
            filename.startswith(pattern) or filename.endswith(pattern)
            for pattern in temp_patterns
        )

    def _is_cache_file(self, filename: str) -> bool:
        """检查是否为缓存文件"""
        cache_patterns = [
            ".coverage",
            "coverage.xml",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "htmlcov",
        ]
        return any(pattern in filename for pattern in cache_patterns)

    def _calculate_file_hash(self, file_path: Path):
        """计算文件哈希值"""
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:  # 跳过大于10MB的文件
                return

            with open(file_path, "rb") as f:
                content = f.read()
                file_hash = hashlib.md5(content).hexdigest()

                if file_hash not in self.file_hashes:
                    self.file_hashes[file_hash] = []
                self.file_hashes[file_hash].append(str(file_path))

        except Exception:
            pass

    def _find_duplicate_files(self):
        """查找重复文件"""
        for file_hash, file_paths in self.file_hashes.items():
            if len(file_paths) > 1:
                # 保留第一个文件，其余标记为重复
                self.redundant_files["duplicate_files"].extend(file_paths[1:])

    def generate_cleanup_report(self) -> str:
        """生成清理报告"""
        report = []
        report.append("# 索克生活 Services 冗余文件清理报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # 统计信息
        total_redundant = sum(len(files) for files in self.redundant_files.values())
        report.append("## 📊 清理统计")
        report.append(f"- 扫描文件总数: {self.cleanup_stats['total_files_scanned']}")
        report.append(f"- 发现冗余文件: {total_redundant}")
        report.append("")

        # 详细分类
        for category, files in self.redundant_files.items():
            if files:
                report.append(
                    f"### {self._get_category_name(category)} ({len(files)}个)"
                )
                for file_path in files[:10]:  # 只显示前10个
                    report.append(f"- {file_path}")
                if len(files) > 10:
                    report.append(f"- ... 还有 {len(files) - 10} 个文件")
                report.append("")

        return "\n".join(report)

    def _get_category_name(self, category: str) -> str:
        """获取分类中文名称"""
        names = {
            "backup_files": "🔄 备份文件",
            "placeholder_files": "📝 占位符文件",
            "duplicate_files": "🔁 重复文件",
            "empty_files": "📄 空文件",
            "temp_files": "🗂️ 临时文件",
            "cache_files": "💾 缓存文件",
        }
        return names.get(category, category)

    def execute_cleanup(self, dry_run: bool = True) -> Dict:
        """执行清理操作"""
        cleanup_results = {
            "removed_files": [],
            "failed_removals": [],
            "total_size_saved": 0,
        }

        if dry_run:
            print("🔍 执行模拟清理 (dry-run模式)")
        else:
            print("🗑️ 执行实际清理")

        for category, files in self.redundant_files.items():
            for file_path in files:
                try:
                    file_path_obj = Path(file_path)
                    if file_path_obj.exists():
                        file_size = file_path_obj.stat().st_size

                        if not dry_run:
                            if file_path_obj.is_file():
                                file_path_obj.unlink()
                            elif file_path_obj.is_dir():
                                shutil.rmtree(file_path_obj)

                        cleanup_results["removed_files"].append(
                            {"path": file_path, "category": category, "size": file_size}
                        )
                        cleanup_results["total_size_saved"] += file_size

                except Exception as e:
                    cleanup_results["failed_removals"].append(
                        {"path": file_path, "error": str(e)}
                    )

        return cleanup_results

    def save_cleanup_record(self, cleanup_results: Dict):
        """保存清理记录"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "scan_results": self.redundant_files,
            "cleanup_results": cleanup_results,
            "stats": self.cleanup_stats,
        }

        record_file = self.services_root / "redundancy_cleanup_record.json"
        with open(record_file, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

        print(f"📝 清理记录已保存到: {record_file}")


def main():
    """主函数"""
    print("🚀 索克生活 Services 智能冗余文件清理器")
    print("=" * 50)

    cleaner = IntelligentRedundancyCleaner()

    # 扫描冗余文件
    redundant_files = cleaner.scan_services()

    # 生成报告
    report = cleaner.generate_cleanup_report()
    print(report)

    # 保存报告
    report_file = Path("services/REDUNDANCY_CLEANUP_REPORT.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"📄 报告已保存到: {report_file}")

    # 询问是否执行清理
    total_files = sum(len(files) for files in redundant_files.values())
    if total_files > 0:
        print(f"\n发现 {total_files} 个冗余文件")

        # 先执行模拟清理
        print("\n执行模拟清理...")
        dry_run_results = cleaner.execute_cleanup(dry_run=True)

        size_mb = dry_run_results["total_size_saved"] / (1024 * 1024)
        print(f"预计可节省空间: {size_mb:.2f} MB")

        # 询问是否执行实际清理
        response = input("\n是否执行实际清理? (y/N): ").strip().lower()
        if response == "y":
            cleanup_results = cleaner.execute_cleanup(dry_run=False)
            cleaner.save_cleanup_record(cleanup_results)
            print("✅ 清理完成!")
        else:
            print("ℹ️ 仅生成报告，未执行清理")
    else:
        print("✨ 未发现冗余文件，services目录很干净!")


if __name__ == "__main__":
    main()
