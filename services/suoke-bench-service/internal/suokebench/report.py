"""
SuokeBench评测报告生成
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import jinja2
from plotly.subplots import make_subplots

from internal.suokebench.config import load_config

logger = logging.getLogger(__name__)

class ReportGenerator:
    """评测报告生成器"""

    def __init__(self, config_path: str = None):
        """
        初始化报告生成器

        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config = load_config(config_path or "config/config.yaml")

        # 加载模板
        self.template_env = self._setup_template_env()

    def _setup_template_env(self) -> jinja2.Environment:
        """
        设置Jinja2模板环境

        Returns:
            模板环境
        """
        # 确保模板目录存在
        template_dir = Path(self.config.report.template_dir)
        if not template_dir.exists():
            # 如果不存在，则使用默认模板
            template_dir = Path(__file__).parent / "templates"

        # 创建模板环境
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate(self, run_id: str, output_format: str = "html") -> str:
        """
        生成评测报告

        Args:
            run_id: 运行ID
            output_format: 输出格式

        Returns:
            报告文件路径
        """
        # 确定数据目录
        data_dir = Path(self.config.report.output_dir) / run_id
        summary_file = data_dir / "summary.json"

        if not summary_file.exists():
            raise FileNotFoundError(f"找不到摘要文件: {summary_file}")

        # 加载摘要数据
        with open(summary_file, encoding="utf-8") as f:
            summary = json.load(f)

        # 准备报告数据
        report_data = self._prepare_report_data(summary, data_dir)

        # 根据格式生成报告
        if output_format == "html":
            return self._generate_html_report(report_data, run_id)
        elif output_format == "pdf":
            return self._generate_pdf_report(report_data, run_id)
        elif output_format == "markdown":
            return self._generate_markdown_report(report_data, run_id)
        elif output_format == "json":
            return self._generate_json_report(report_data, run_id)
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")

    def _prepare_report_data(
        self, summary: dict[str, Any], data_dir: Path
    ) -> dict[str, Any]:
        """
        准备报告数据

        Args:
            summary: 摘要数据
            data_dir: 数据目录

        Returns:
            报告数据
        """
        # 计算总体指标
        metrics_summary = self._calculate_metrics_summary(summary)

        # 生成图表数据
        if self.config.report.include_plots:
            plots = self._generate_plots(summary, metrics_summary, data_dir)
        else:
            plots = {}

        # 构建报告数据
        report_data = {
            "title": f"{self.config.report.title_prefix} - {summary['run_id']}",
            "timestamp": datetime.fromtimestamp(summary["timestamp"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "run_id": summary["run_id"],
            "summary": summary,
            "metrics_summary": metrics_summary,
            "plots": plots,
            "config": {
                "service_name": self.config.service_name,
                "version": self.config.version,
            },
        }

        return report_data

    def _calculate_metrics_summary(self, summary: dict[str, Any]) -> dict[str, Any]:
        """
        计算总体指标摘要

        Args:
            summary: 摘要数据

        Returns:
            指标摘要
        """
        # 初始化指标摘要
        metrics_summary = {
            "overall": {
                "tasks": summary["tasks"],
                "success": summary["success"],
                "failed": summary["failed"],
                "success_rate": summary["success"] / summary["tasks"]
                if summary["tasks"] > 0
                else 0,
            },
            "metrics": {},
        }

        # 处理每个任务的指标
        for _task_id, result in summary["results"].items():
            if result.get("status") != "SUCCESS":
                continue

            for metric_name, metric_value in result.get("metrics", {}).items():
                if isinstance(metric_value, int | float):
                    # 添加到总体指标
                    if metric_name not in metrics_summary["metrics"]:
                        metrics_summary["metrics"][metric_name] = {
                            "values": [],
                            "avg": 0,
                            "min": float("inf"),
                            "max": float("-inf"),
                        }

                    metrics_summary["metrics"][metric_name]["values"].append(
                        metric_value
                    )

                    # 更新统计值
                    values = metrics_summary["metrics"][metric_name]["values"]
                    metrics_summary["metrics"][metric_name]["avg"] = sum(values) / len(
                        values
                    )
                    metrics_summary["metrics"][metric_name]["min"] = min(values)
                    metrics_summary["metrics"][metric_name]["max"] = max(values)

        return metrics_summary

    def _generate_plots(
        self, summary: dict[str, Any], metrics_summary: dict[str, Any], data_dir: Path
    ) -> dict[str, str]:
        """
        生成图表

        Args:
            summary: 摘要数据
            metrics_summary: 指标摘要
            data_dir: 数据目录

        Returns:
            图表数据
        """
        plots = {}

        # 生成总体指标图表
        plots["overall_metrics"] = self._generate_overall_metrics_plot(metrics_summary)

        # 生成任务成功率图表
        plots["task_success_rate"] = self._generate_task_success_plot(summary)

        # 保存图表
        plots_dir = data_dir / "plots"
        plots_dir.mkdir(exist_ok=True)

        # 保存为HTML文件
        for plot_name, plot_html in plots.items():
            plot_file = plots_dir / f"{plot_name}.html"
            with open(plot_file, "w", encoding="utf-8") as f:
                f.write(plot_html)

        return plots

    def _generate_overall_metrics_plot(self, metrics_summary: dict[str, Any]) -> str:
        """
        生成总体指标图表

        Args:
            metrics_summary: 指标摘要

        Returns:
            图表HTML
        """
        if not metrics_summary["metrics"]:
            return ""

        # 创建图表
        fig = make_subplots(rows=1, cols=1)

        # 添加指标数据
        metrics = []
        values = []

        for metric_name, metric_data in metrics_summary["metrics"].items():
            metrics.append(metric_name)
            values.append(metric_data["avg"])

        # 创建条形图
        fig.add_trace(
            go.Bar(
                x=metrics,
                y=values,
                name="平均值",
                text=values,
                textposition="auto",
            )
        )

        # 设置布局
        fig.update_layout(
            title="总体指标摘要",
            xaxis_title="指标",
            yaxis_title="值",
            height=500,
        )

        # 转换为HTML
        return fig.to_html(include_plotlyjs="cdn")

    def _generate_task_success_plot(self, summary: dict[str, Any]) -> str:
        """
        生成任务成功率图表

        Args:
            summary: 摘要数据

        Returns:
            图表HTML
        """
        # 准备数据
        task_ids = []
        statuses = []

        for task_id, result in summary["results"].items():
            task_ids.append(task_id)
            statuses.append(result.get("status", "UNKNOWN"))

        # 创建饼图
        fig = px.pie(
            names=["SUCCESS", "ERROR", "UNKNOWN"],
            values=[
                sum(1 for s in statuses if s == "SUCCESS"),
                sum(1 for s in statuses if s == "ERROR"),
                sum(1 for s in statuses if s not in ["SUCCESS", "ERROR"]),
            ],
            title="任务成功率",
        )

        # 设置布局
        fig.update_layout(height=400)

        # 转换为HTML
        return fig.to_html(include_plotlyjs="cdn")

    def _generate_html_report(self, report_data: dict[str, Any], run_id: str) -> str:
        """
        生成HTML报告

        Args:
            report_data: 报告数据
            run_id: 运行ID

        Returns:
            报告文件路径
        """
        # 加载模板
        template = self.template_env.get_template("report.html")

        # 渲染模板
        html = template.render(**report_data)

        # 保存报告
        report_file = Path(self.config.report.output_dir) / run_id / "report.html"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html)

        return str(report_file)

    def _generate_pdf_report(self, report_data: dict[str, Any], run_id: str) -> str:
        """
        生成PDF报告

        Args:
            report_data: 报告数据
            run_id: 运行ID

        Returns:
            报告文件路径
        """
        # 需要安装额外依赖
        # pip install weasyprint 或 使用其他HTML到PDF的转换库
        try:
            import weasyprint
        except ImportError:
            logger.error("生成PDF报告需要安装weasyprint库")
            raise

        # 先生成HTML
        html_path = self._generate_html_report(report_data, run_id)

        # 转换为PDF
        pdf_path = str(html_path).replace(".html", ".pdf")

        # 使用weasyprint转换
        weasyprint.HTML(html_path).write_pdf(pdf_path)

        return pdf_path

    def _generate_markdown_report(
        self, report_data: dict[str, Any], run_id: str
    ) -> str:
        """
        生成Markdown报告

        Args:
            report_data: 报告数据
            run_id: 运行ID

        Returns:
            报告文件路径
        """
        # 加载模板
        template = self.template_env.get_template("report.md")

        # 渲染模板
        markdown = template.render(**report_data)

        # 保存报告
        report_file = Path(self.config.report.output_dir) / run_id / "report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(markdown)

        return str(report_file)

    def _generate_json_report(self, report_data: dict[str, Any], run_id: str) -> str:
        """
        生成JSON报告

        Args:
            report_data: 报告数据
            run_id: 运行ID

        Returns:
            报告文件路径
        """
        # 保存报告
        report_file = Path(self.config.report.output_dir) / run_id / "report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        return str(report_file)

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="SuokeBench评测报告生成")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--run-id", type=str, required=True, help="运行ID")
    parser.add_argument(
        "--format",
        type=str,
        default="html",
        choices=["html", "pdf", "markdown", "json"],
        help="输出格式",
    )
    args = parser.parse_args()

    # 创建并运行报告生成器
    generator = ReportGenerator(args.config)
    report_path = generator.generate(args.run_id, args.format)

    print(f"报告已生成: {report_path}")

if __name__ == "__main__":
    main()
