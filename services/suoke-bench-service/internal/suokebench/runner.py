"""
runner - 索克生活项目模块
"""

        import json
from internal.suokebench.config import BenchConfig, load_config
from pathlib import Path
from typing import Any
import argparse
import logging
import sys
import time

"""
SuokeBench评测运行器
"""



logger = logging.getLogger(__name__)


class SuokeBenchRunner:
    """SuokeBench评测运行器"""

    def __init__(self, config_path: str = None, is_ci: bool = False):
        """
        初始化评测运行器

        Args:
            config_path: 配置文件路径
            is_ci: 是否为CI环境
        """
        # 加载配置
        self.config = load_config(config_path or "config/config.yaml")
        self.is_ci = is_ci

        # 创建运行ID
        timestamp = int(time.time())
        self.run_id = f"run_{timestamp}"

        # 创建输出目录
        self.output_dir = Path(self.config.report.output_dir) / self.run_id
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 设置日志
        self._setup_logging()

    def _setup_logging(self):
        """设置日志"""
        log_file = self.output_dir / "run.log"

        # 配置日志格式
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        log_level = getattr(logging, self.config.log_level)

        # 创建处理器
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(log_format))

        # 配置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    def run(self):
        """运行所有评测任务"""
        logger.info(f"开始运行评测：{self.run_id}")

        # 确定要运行的任务
        tasks = self._get_tasks()

        if not tasks:
            logger.warning("没有找到可运行的任务")
            return

        # 运行任务
        results = {}
        for task_id, task in tasks.items():
            logger.info(f"运行任务：{task_id}")

            try:
                # 加载任务模块
                task_runner = self._load_task_runner(task_id)

                # 执行任务
                task_result = task_runner.run(task, self.config)

                # 保存结果
                results[task_id] = task_result

                # 保存任务结果
                self._save_task_result(task_id, task_result)

                logger.info(f"任务 {task_id} 完成")

            except Exception as e:
                logger.error(f"任务 {task_id} 失败: {str(e)}", exc_info=True)

                # 记录错误
                results[task_id] = {
                    "status": "ERROR",
                    "error": str(e),
                }

        # 生成总体报告
        self._generate_report(results)

        logger.info(f"评测运行完成：{self.run_id}")

    def _get_tasks(self) -> dict[str, Any]:
        """
        获取要运行的任务

        Returns:
            任务字典
        """
        # 在CI模式下，只运行部分关键任务
        if self.is_ci:
            ci_tasks = {}
            # 选择最重要的任务（简化版）
            for task_id, task in self.config.tasks.items():
                if task.priority >= 8:  # 高优先级任务
                    ci_tasks[task_id] = task
            return ci_tasks

        # 否则运行所有任务
        return self.config.tasks

    def _load_task_runner(self, task_id: str) -> Any:
        """
        加载任务运行器

        Args:
            task_id: 任务ID

        Returns:
            任务运行器实例
        """
        # 获取任务类型
        self.config.tasks[task_id].type

        # 根据任务类型加载相应的运行器
        # 实际项目中应使用动态导入或工厂模式
        # 这里简化为返回一个通用运行器
        return DummyTaskRunner()

    def _save_task_result(self, task_id: str, result: dict[str, Any]):
        """
        保存任务结果

        Args:
            task_id: 任务ID
            result: 任务结果
        """

        # 保存结果到JSON文件
        result_file = self.output_dir / f"{task_id}_result.json"

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    def _generate_report(self, results: dict[str, dict[str, Any]]):
        """
        生成评测报告

        Args:
            results: 所有任务的结果
        """

        # 保存总体结果
        summary_file = self.output_dir / "summary.json"

        # 构建摘要
        summary = {
            "run_id": self.run_id,
            "timestamp": int(time.time()),
            "tasks": len(results),
            "success": sum(1 for r in results.values() if r.get("status") == "SUCCESS"),
            "failed": sum(1 for r in results.values() if r.get("status") == "ERROR"),
            "results": results,
        }

        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        # 实际项目中应生成HTML或其他格式的报告
        logger.info(f"评测报告已保存到：{self.output_dir}")


class DummyTaskRunner:
    """简单的任务运行器实现"""

    def run(self, task_config: Any, config: BenchConfig) -> dict[str, Any]:
        """
        运行任务

        Args:
            task_config: 任务配置
            config: 总体配置

        Returns:
            任务结果
        """
        # 模拟任务运行
        time.sleep(2)

        # 返回模拟结果
        return {
            "status": "SUCCESS",
            "task_id": task_config.id,
            "metrics": {
                "accuracy": 0.85,
                "f1": 0.82,
            },
            "samples_processed": 100,
            "duration_seconds": 2,
        }


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="SuokeBench评测运行器")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--ci", action="store_true", help="是否为CI环境")
    args = parser.parse_args()

    # 创建并运行评测
    runner = SuokeBenchRunner(args.config, args.ci)
    runner.run()


if __name__ == "__main__":
    main()
