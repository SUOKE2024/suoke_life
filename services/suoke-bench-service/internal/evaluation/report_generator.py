"""
评测报告生成器

用于生成详细、美观的评测报告。
"""

import json
import logging
import os
from datetime import datetime
from typing import Any

import jinja2
import pandas as pd
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


class ReportGenerator:
    """评测报告生成器"""

    def __init__(self, output_dir: str = "data/reports"):
        """
        初始化报告生成器

        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = output_dir

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 加载模板
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("internal/evaluation/templates"),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_report(
        self,
        result: dict[str, Any],
        format: str = "html",
        include_samples: bool = True,
        include_metrics: list[str] | None = None,
    ) -> str:
        """
        生成评测报告

        Args:
            result: 评测结果
            format: 报告格式（html, pdf, markdown, json）
            include_samples: 是否包含样本详情
            include_metrics: 要包含的指标，None表示包含所有指标

        Returns:
            报告文件路径
        """
        # 准备报告数据
        report_data = self._prepare_report_data(
            result, include_samples, include_metrics
        )

        # 根据格式生成报告
        if format == "html":
            return self._generate_html_report(report_data)
        elif format == "pdf":
            return self._generate_pdf_report(report_data)
        elif format == "markdown":
            return self._generate_markdown_report(report_data)
        elif format == "json":
            return self._generate_json_report(report_data)
        else:
            logger.error(f"不支持的报告格式: {format}")
            return ""

    def _prepare_report_data(
        self,
        result: dict[str, Any],
        include_samples: bool,
        include_metrics: list[str] | None,
    ) -> dict[str, Any]:
        """
        准备报告数据

        Args:
            result: 评测结果
            include_samples: 是否包含样本详情
            include_metrics: 要包含的指标

        Returns:
            处理后的报告数据
        """
        report_data = {
            "title": f"索克评测报告 - {result.get('benchmark_id', '未知测试')}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "run_id": result.get("run_id", "未知"),
            "benchmark_id": result.get("benchmark_id", "未知"),
            "model_id": result.get("model_id", "未知"),
            "model_version": result.get("model_version", "未知"),
            "status": result.get("status", "未知"),
            "created_at": result.get("created_at", ""),
            "completed_at": result.get("completed_at", ""),
            "metrics": [],
            "samples": [],
            "charts": {},
            "summary": "",
        }

        # 处理指标
        metrics = result.get("metrics", {})
        if include_metrics:
            # 只包含指定的指标
            metrics = {k: v for k, v in metrics.items() if k in include_metrics}

        # 格式化指标
        for name, metric in metrics.items():
            value = metric.get("value", 0)
            threshold = metric.get("threshold", 0)
            passed = metric.get("pass", value >= threshold)

            report_data["metrics"].append(
                {
                    "name": name,
                    "display_name": metric.get("display_name", name),
                    "value": value,
                    "unit": metric.get("unit", ""),
                    "threshold": threshold,
                    "pass": passed,
                    "higher_is_better": metric.get("higher_is_better", True),
                    "comparison": metric.get("comparison", ""),
                }
            )

        # 生成性能总览
        passing_count = sum(1 for m in report_data["metrics"] if m["pass"])
        total_count = len(report_data["metrics"])
        report_data["passing_rate"] = (
            passing_count / total_count if total_count > 0 else 0
        )

        # 处理样本（如果需要）
        if include_samples and "samples" in result:
            for sample in result["samples"]:
                report_data["samples"].append(
                    {
                        "id": sample.get("id", ""),
                        "input": sample.get("input", ""),
                        "expected": sample.get("expected", ""),
                        "actual": sample.get("actual", ""),
                        "correct": sample.get("correct", False),
                        "scores": sample.get("scores", {}),
                    }
                )

        # 生成图表数据
        report_data["charts"] = self._generate_chart_data(report_data)

        # 生成总结
        report_data["summary"] = self._generate_summary(report_data)

        return report_data

    def _generate_chart_data(self, report_data: dict[str, Any]) -> dict[str, Any]:
        """
        生成图表数据

        Args:
            report_data: 报告数据

        Returns:
            图表数据
        """
        charts = {}

        # 指标性能柱状图
        metrics_df = pd.DataFrame(report_data["metrics"])
        if not metrics_df.empty:
            # 按值排序
            metrics_df = metrics_df.sort_values("value", ascending=False)

            # 创建柱状图
            fig = go.Figure()

            for _, row in metrics_df.iterrows():
                color = "green" if row["pass"] else "red"
                fig.add_trace(
                    go.Bar(
                        x=[row["display_name"]],
                        y=[row["value"]],
                        name=row["display_name"],
                        marker_color=color,
                        text=[f"{row['value']:.2f}{row['unit']}"],
                        textposition="auto",
                    )
                )

                # 添加阈值线
                fig.add_trace(
                    go.Scatter(
                        x=[row["display_name"]],
                        y=[row["threshold"]],
                        mode="markers",
                        marker={
                            "symbol": "line-ew",
                            "size": 40,
                            "color": "rgba(0, 0, 0, 0.7)",
                            "line": {"width": 2, "color": "black"},
                        },
                        name=f"阈值: {row['threshold']}{row['unit']}",
                        showlegend=False,
                    )
                )

            fig.update_layout(
                title="指标性能对比",
                xaxis_title="指标",
                yaxis_title="值",
                barmode="group",
                template="plotly_white",
            )

            charts["metrics_bar"] = fig.to_json()

        # 如果有样本，生成准确率饼图
        if report_data["samples"]:
            correct_count = sum(1 for s in report_data["samples"] if s["correct"])
            incorrect_count = len(report_data["samples"]) - correct_count

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=["正确", "错误"],
                        values=[correct_count, incorrect_count],
                        hole=0.3,
                        marker={"colors": ["green", "red"]},
                    )
                ]
            )

            fig.update_layout(
                title="样本预测结果",
                template="plotly_white",
            )

            charts["samples_pie"] = fig.to_json()

        return charts

    def _generate_summary(self, report_data: dict[str, Any]) -> str:
        """
        生成评测总结

        Args:
            report_data: 报告数据

        Returns:
            总结文本
        """
        model_id = report_data["model_id"]
        model_version = report_data["model_version"]
        benchmark_id = report_data["benchmark_id"]
        passing_rate = report_data["passing_rate"]
        metrics_count = len(report_data["metrics"])

        # 计算性能等级
        if passing_rate >= 0.9:
            performance_level = "优秀"
        elif passing_rate >= 0.8:
            performance_level = "良好"
        elif passing_rate >= 0.7:
            performance_level = "合格"
        else:
            performance_level = "不达标"

        # 查找最佳和最差指标
        metrics = report_data["metrics"]
        if metrics:
            # 根据是否越高越好排序
            best_metric = None
            worst_metric = None

            for metric in metrics:
                normalized_value = (
                    metric["value"] / metric["threshold"]
                    if metric["threshold"] > 0
                    else 0
                )

                if (
                    not best_metric
                    or (
                        metric["higher_is_better"]
                        and normalized_value > best_metric["normalized_value"]
                    )
                    or (
                        not metric["higher_is_better"]
                        and normalized_value < best_metric["normalized_value"]
                    )
                ):
                    best_metric = {
                        "name": metric["display_name"],
                        "value": metric["value"],
                        "unit": metric["unit"],
                        "normalized_value": normalized_value,
                    }

                if (
                    not worst_metric
                    or (
                        metric["higher_is_better"]
                        and normalized_value < worst_metric["normalized_value"]
                    )
                    or (
                        not metric["higher_is_better"]
                        and normalized_value > worst_metric["normalized_value"]
                    )
                ):
                    worst_metric = {
                        "name": metric["display_name"],
                        "value": metric["value"],
                        "unit": metric["unit"],
                        "normalized_value": normalized_value,
                    }

            best_metric_text = (
                f"{best_metric['name']}（{best_metric['value']}{best_metric['unit']}）"
                if best_metric
                else "无"
            )
            worst_metric_text = (
                f"{worst_metric['name']}（{worst_metric['value']}{worst_metric['unit']}）"
                if worst_metric
                else "无"
            )
        else:
            best_metric_text = "无"
            worst_metric_text = "无"

        # 生成总结文本
        summary = (
            f"模型 {model_id}:{model_version} 在 {benchmark_id} 评测中的整体表现为{performance_level}，"
            f"通过率为 {passing_rate:.2%}（{int(passing_rate * metrics_count)}/{metrics_count}）。"
        )

        if best_metric_text != "无":
            summary += f" 表现最佳的指标是{best_metric_text}，表现最差的指标是{worst_metric_text}。"

        # 添加改进建议
        if passing_rate < 0.7:
            summary += " 建议重点改进模型在关键指标上的表现，特别是未通过阈值的指标。"
        elif passing_rate < 0.9:
            summary += (
                " 模型整体表现良好，但仍有提升空间，建议针对表现较差的指标进行优化。"
            )
        else:
            summary += " 模型表现优秀，可以考虑进一步优化性能或扩展模型能力。"

        return summary

    def _generate_html_report(self, report_data: dict[str, Any]) -> str:
        """
        生成HTML报告

        Args:
            report_data: 报告数据

        Returns:
            报告文件路径
        """
        try:
            # 加载模板
            template = self.jinja_env.get_template("report.html")

            # 渲染报告
            html_content = template.render(**report_data)

            # 保存报告
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"report_{report_data['run_id']}_{timestamp}.html"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"HTML报告已生成: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"生成HTML报告失败: {str(e)}")
            return ""

    def _generate_pdf_report(self, report_data: dict[str, Any]) -> str:
        """
        生成PDF报告

        Args:
            report_data: 报告数据

        Returns:
            报告文件路径
        """
        try:
            # 首先生成HTML报告
            html_path = self._generate_html_report(report_data)
            if not html_path:
                logger.error("生成HTML报告失败，无法转换为PDF")
                return ""

            # 生成PDF文件路径
            pdf_path = html_path.replace(".html", ".pdf")

            try:
                # 使用weasyprint转换HTML为PDF
                from weasyprint import HTML

                HTML(html_path).write_pdf(pdf_path)

                logger.info(f"PDF报告已生成: {pdf_path}")
                return pdf_path
            except ImportError:
                logger.error("未安装weasyprint，无法生成PDF报告")
                return html_path
        except Exception as e:
            logger.error(f"生成PDF报告失败: {str(e)}")
            return ""

    def _generate_markdown_report(self, report_data: dict[str, Any]) -> str:
        """
        生成Markdown报告

        Args:
            report_data: 报告数据

        Returns:
            报告文件路径
        """
        try:
            # 加载模板
            template = self.jinja_env.get_template("report.md")

            # 渲染报告
            md_content = template.render(**report_data)

            # 保存报告
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"report_{report_data['run_id']}_{timestamp}.md"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_content)

            logger.info(f"Markdown报告已生成: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"生成Markdown报告失败: {str(e)}")
            return ""

    def _generate_json_report(self, report_data: dict[str, Any]) -> str:
        """
        生成JSON报告

        Args:
            report_data: 报告数据

        Returns:
            报告文件路径
        """
        try:
            # 准备JSON数据
            json_data = {
                "title": report_data["title"],
                "timestamp": report_data["timestamp"],
                "run_id": report_data["run_id"],
                "benchmark_id": report_data["benchmark_id"],
                "model_id": report_data["model_id"],
                "model_version": report_data["model_version"],
                "status": report_data["status"],
                "created_at": report_data["created_at"],
                "completed_at": report_data["completed_at"],
                "metrics": report_data["metrics"],
                "passing_rate": report_data["passing_rate"],
                "summary": report_data["summary"],
            }

            # 如果包含样本，添加样本数据
            if report_data["samples"]:
                json_data["samples"] = report_data["samples"]

            # 保存报告
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"report_{report_data['run_id']}_{timestamp}.json"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            logger.info(f"JSON报告已生成: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"生成JSON报告失败: {str(e)}")
            return ""
