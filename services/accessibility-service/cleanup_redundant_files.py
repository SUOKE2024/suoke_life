#!/usr/bin/env python3
"""
索克生活无障碍服务 - 冗余文件清理脚本

该脚本用于清理代码库中的冗余文件，包括：
1. 临时报告文件
2. 空的Python文件
3. Python缓存目录
4. 重复的配置文件
5. 过时的测试文件

遵循Python 3.13.3和最佳实践
"""

import glob
import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("cleanup.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class RedundantFilesCleaner:
    """冗余文件清理器"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.cleanup_report = {
            "timestamp": datetime.now().isoformat(),
            "cleaned_files": [],
            "cleaned_directories": [],
            "preserved_files": [],
            "errors": [],
            "statistics": {
                "total_files_removed": 0,
                "total_directories_removed": 0,
                "space_saved_mb": 0,
            },
        }

    def clean_temporary_reports(self) -> None:
        """清理临时报告文件"""
        logger.info("🧹 开始清理临时报告文件...")

        # 清理快速验证报告（保留最新的2个）
        quick_reports = sorted(glob.glob("quick_validation_report_*.json"))
        if len(quick_reports) > 2:
            for report in quick_reports[:-2]:
                self._remove_file(report, "临时快速验证报告")

        # 清理简单验证报告（保留最新的2个）
        simple_reports = sorted(glob.glob("simple_validation_report_*.json"))
        if len(simple_reports) > 2:
            for report in simple_reports[:-2]:
                self._remove_file(report, "临时简单验证报告")

        # 清理其他临时文件
        temp_patterns = ["*.tmp", "*.temp", "*.bak", "*.orig", ".DS_Store"]

        for pattern in temp_patterns:
            for file_path in glob.glob(pattern, recursive=True):
                self._remove_file(file_path, f"临时文件 ({pattern})")

    def clean_empty_files(self) -> None:
        """清理空文件"""
        logger.info("🧹 开始清理空文件...")

        empty_files = [
            "./test/test_simple_e2e.py",
            "./internal/service/optimized_example.py",
            "./accessibility_service_100_percent_completion.py",
        ]

        for file_path in empty_files:
            if os.path.exists(file_path) and os.path.getsize(file_path) == 0:
                self._remove_file(file_path, "空Python文件")

        # 查找其他空的Python文件
        for py_file in glob.glob("**/*.py", recursive=True):
            if os.path.getsize(py_file) == 0 and not py_file.startswith(".venv/"):
                self._remove_file(py_file, "空Python文件")

    def clean_pycache_directories(self) -> None:
        """清理Python缓存目录"""
        logger.info("🧹 开始清理Python缓存目录...")

        for pycache_dir in glob.glob("**/__pycache__", recursive=True):
            if not pycache_dir.startswith(".venv/"):
                self._remove_directory(pycache_dir, "Python缓存目录")

        # 清理.pyc文件
        for pyc_file in glob.glob("**/*.pyc", recursive=True):
            if not pyc_file.startswith(".venv/"):
                self._remove_file(pyc_file, "Python字节码文件")

    def clean_duplicate_configs(self) -> None:
        """处理重复的配置文件"""
        logger.info("🧹 检查重复的配置文件...")

        config_files = ["config/config.py", "config/enhanced_config.py"]

        # 检查文件是否存在且内容相似
        existing_configs = [f for f in config_files if os.path.exists(f)]

        if len(existing_configs) > 1:
            logger.warning(f"发现重复的配置文件: {existing_configs}")
            logger.warning("请手动检查并合并这些配置文件")
            self.cleanup_report["preserved_files"].extend(existing_configs)

    def clean_redundant_test_files(self) -> None:
        """清理冗余的测试文件"""
        logger.info("🧹 检查冗余的测试文件...")

        # 查找可能重复的测试文件
        test_patterns = [
            "test_*_simple.py",
            "test_*_enhanced.py",
            "test_*_optimized.py",
        ]

        for pattern in test_patterns:
            test_files = glob.glob(f"test/{pattern}")
            if len(test_files) > 1:
                logger.warning(f"发现可能重复的测试文件: {test_files}")
                logger.warning("请手动检查并整合这些测试文件")
                self.cleanup_report["preserved_files"].extend(test_files)

    def clean_log_files(self) -> None:
        """清理旧的日志文件"""
        logger.info("🧹 清理旧的日志文件...")

        log_patterns = ["*.log", "logs/*.log", "validation.log"]

        for pattern in log_patterns:
            for log_file in glob.glob(pattern):
                # 保留最近的日志文件
                if os.path.getmtime(log_file) < (
                    datetime.now().timestamp() - 7 * 24 * 3600
                ):
                    self._remove_file(log_file, "旧日志文件")

    def optimize_gitignore(self) -> None:
        """优化.gitignore文件"""
        logger.info("🧹 优化.gitignore文件...")

        gitignore_additions = [
            "# Python缓存",
            "__pycache__/",
            "*.py[cod]",
            "*$py.class",
            "",
            "# 临时文件",
            "*.tmp",
            "*.temp",
            "*.bak",
            "*.orig",
            "",
            "# 报告文件",
            "*_report_*.json",
            "*_validation_*.json",
            "",
            "# 日志文件",
            "*.log",
            "logs/",
            "",
            "# 系统文件",
            ".DS_Store",
            "Thumbs.db",
            "",
            "# IDE文件",
            ".vscode/",
            ".idea/",
            "*.swp",
            "*.swo",
        ]

        gitignore_path = ".gitignore"
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r", encoding="utf-8") as f:
                existing_content = f.read()

            # 检查是否需要添加新规则
            new_rules = []
            for rule in gitignore_additions:
                if rule and rule not in existing_content:
                    new_rules.append(rule)

            if new_rules:
                with open(gitignore_path, "a", encoding="utf-8") as f:
                    f.write("\n# 自动添加的清理规则\n")
                    f.write("\n".join(new_rules))
                    f.write("\n")
                logger.info(f"已向.gitignore添加 {len(new_rules)} 条新规则")

    def _remove_file(self, file_path: str, file_type: str) -> None:
        """安全删除文件"""
        try:
            file_size = os.path.getsize(file_path)
            os.remove(file_path)

            self.cleanup_report["cleaned_files"].append(
                {"path": file_path, "type": file_type, "size_bytes": file_size}
            )
            self.cleanup_report["statistics"]["total_files_removed"] += 1
            self.cleanup_report["statistics"]["space_saved_mb"] += file_size / (
                1024 * 1024
            )

            logger.info(f"✅ 已删除{file_type}: {file_path}")

        except Exception as e:
            error_msg = f"删除文件失败 {file_path}: {e}"
            logger.error(error_msg)
            self.cleanup_report["errors"].append(error_msg)

    def _remove_directory(self, dir_path: str, dir_type: str) -> None:
        """安全删除目录"""
        try:
            # 计算目录大小
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(dir_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)

            shutil.rmtree(dir_path)

            self.cleanup_report["cleaned_directories"].append(
                {"path": dir_path, "type": dir_type, "size_bytes": total_size}
            )
            self.cleanup_report["statistics"]["total_directories_removed"] += 1
            self.cleanup_report["statistics"]["space_saved_mb"] += total_size / (
                1024 * 1024
            )

            logger.info(f"✅ 已删除{dir_type}: {dir_path}")

        except Exception as e:
            error_msg = f"删除目录失败 {dir_path}: {e}"
            logger.error(error_msg)
            self.cleanup_report["errors"].append(error_msg)

    def generate_report(self) -> None:
        """生成清理报告"""
        report_file = f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(self.cleanup_report, f, indent=2, ensure_ascii=False)

            logger.info(f"📊 清理报告已生成: {report_file}")

            # 打印统计信息
            stats = self.cleanup_report["statistics"]
            logger.info("📈 清理统计:")
            logger.info(f"   删除文件数: {stats['total_files_removed']}")
            logger.info(f"   删除目录数: {stats['total_directories_removed']}")
            logger.info(f"   节省空间: {stats['space_saved_mb']:.2f} MB")

            if self.cleanup_report["errors"]:
                logger.warning(f"⚠️  发生 {len(self.cleanup_report['errors'])} 个错误")

        except Exception as e:
            logger.error(f"生成报告失败: {e}")

    def run_cleanup(self) -> None:
        """执行完整的清理流程"""
        logger.info("🚀 开始执行冗余文件清理...")

        try:
            self.clean_temporary_reports()
            self.clean_empty_files()
            self.clean_pycache_directories()
            self.clean_duplicate_configs()
            self.clean_redundant_test_files()
            self.clean_log_files()
            self.optimize_gitignore()

            logger.info("✅ 清理流程完成")

        except Exception as e:
            logger.error(f"清理过程中发生错误: {e}")
            self.cleanup_report["errors"].append(str(e))

        finally:
            self.generate_report()


def main() -> None:
    """主函数"""
    print("🧹 索克生活无障碍服务 - 冗余文件清理工具")
    print("=" * 50)

    # 确认清理操作
    response = input("⚠️  此操作将删除冗余文件，是否继续？(y/N): ")
    if response.lower() != "y":
        print("❌ 清理操作已取消")
        return

    # 执行清理
    cleaner = RedundantFilesCleaner()
    cleaner.run_cleanup()

    print("🎉 清理完成！请查看生成的报告文件了解详情。")


if __name__ == "__main__":
    main()
