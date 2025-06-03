#!/usr/bin/env python3

"""
高级数据可视化模块
提供丰富的图表和可视化功能，支持实时数据展示、交互式图表和多维度分析
包含脉象波形、健康趋势、体质分析、风险评估等多种可视化组件
"""

import base64
import colorsys
import io
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from plotly.subplots import make_subplots
from scipy import signal
from scipy.fft import fft, fftfreq

# 设置中文字体
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

logger = logging.getLogger(__name__)

class ChartType(Enum):
    """图表类型枚举"""

    LINE = "line"  # 线图
    BAR = "bar"  # 柱状图
    SCATTER = "scatter"  # 散点图
    HEATMAP = "heatmap"  # 热力图
    RADAR = "radar"  # 雷达图
    GAUGE = "gauge"  # 仪表盘
    WAVEFORM = "waveform"  # 波形图
    SPECTRUM = "spectrum"  # 频谱图
    TREEMAP = "treemap"  # 树状图
    SANKEY = "sankey"  # 桑基图
    WATERFALL = "waterfall"  # 瀑布图
    VIOLIN = "violin"  # 小提琴图

class VisualizationStyle(Enum):
    """可视化风格枚举"""

    MEDICAL = "medical"  # 医疗风格
    MODERN = "modern"  # 现代风格
    CLASSIC = "classic"  # 经典风格
    DARK = "dark"  # 暗色风格
    COLORFUL = "colorful"  # 彩色风格

class InteractionMode(Enum):
    """交互模式枚举"""

    STATIC = "static"  # 静态
    INTERACTIVE = "interactive"  # 交互式
    ANIMATED = "animated"  # 动画
    REAL_TIME = "real_time"  # 实时

@dataclass
class ChartConfig:
    """图表配置"""

    chart_type: ChartType
    title: str
    width: int = 800
    height: int = 600
    style: VisualizationStyle = VisualizationStyle.MEDICAL
    interaction_mode: InteractionMode = InteractionMode.STATIC
    color_scheme: list[str] | None = None
    show_legend: bool = True
    show_grid: bool = True
    animation_duration: int = 1000  # 毫秒
    update_interval: int = 100  # 毫秒
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class VisualizationResult:
    """可视化结果"""

    chart_id: str
    chart_type: ChartType
    html_content: str | None = None
    base64_image: str | None = None
    interactive_data: dict[str, Any] | None = None
    file_path: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

class AdvancedVisualizer:
    """高级数据可视化器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化高级数据可视化器

        Args:
            config: 配置字典
        """
        self.config = config

        # 基础配置
        self.output_dir = config.get("output_dir", "output/visualizations")
        self.default_style = VisualizationStyle(config.get("default_style", "medical"))
        self.default_dpi = config.get("default_dpi", 300)
        self.default_figsize = tuple(config.get("default_figsize", [12, 8]))

        # 颜色配置
        self.color_schemes = {
            VisualizationStyle.MEDICAL: ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#6A994E"],
            VisualizationStyle.MODERN: ["#264653", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51"],
            VisualizationStyle.CLASSIC: ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
            VisualizationStyle.DARK: ["#BB86FC", "#03DAC6", "#CF6679", "#FF6B6B", "#4ECDC4"],
            VisualizationStyle.COLORFUL: ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"],
        }

        # 中医相关颜色
        self.tcm_colors = {
            "qi": "#4CAF50",  # 气 - 绿色
            "blood": "#F44336",  # 血 - 红色
            "yin": "#2196F3",  # 阴 - 蓝色
            "yang": "#FF9800",  # 阳 - 橙色
            "heart": "#E91E63",  # 心 - 粉红
            "liver": "#4CAF50",  # 肝 - 绿色
            "spleen": "#FFEB3B",  # 脾 - 黄色
            "lung": "#FFFFFF",  # 肺 - 白色
            "kidney": "#000000",  # 肾 - 黑色
        }

        # 实时数据缓存
        self.real_time_data = {}
        self.animation_objects = {}

        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=4)

        # 初始化组件
        self._initialize_components()

        logger.info("高级数据可视化器初始化完成")

    def _initialize_components(self):
        """初始化组件"""
        try:
            # 创建输出目录
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)

            # 设置matplotlib样式
            plt.style.use("default")
            sns.set_palette("husl")

            # 设置plotly默认配置
            pyo.init_notebook_mode(connected=True)

            logger.info("可视化组件初始化完成")

        except Exception as e:
            logger.error(f"组件初始化失败: {e}")
            raise

    async def create_pulse_waveform_chart(
        self, pulse_data: list[float], sampling_rate: int = 1000, config: ChartConfig | None = None
    ) -> VisualizationResult:
        """
        创建脉搏波形图

        Args:
            pulse_data: 脉搏数据
            sampling_rate: 采样率
            config: 图表配置

        Returns:
            可视化结果
        """
        try:
            if config is None:
                config = ChartConfig(
                    chart_type=ChartType.WAVEFORM, title="脉搏波形分析", width=1200, height=400
                )

            # 生成时间轴
            time_axis = np.arange(len(pulse_data)) / sampling_rate

            if config.interaction_mode == InteractionMode.INTERACTIVE:
                # 创建交互式图表
                fig = go.Figure()

                # 添加原始波形
                fig.add_trace(
                    go.Scatter(
                        x=time_axis,
                        y=pulse_data,
                        mode="lines",
                        name="脉搏波形",
                        line=dict(color="#2E86AB", width=2),
                    )
                )

                # 检测峰值
                peaks, _ = signal.find_peaks(
                    pulse_data, height=np.mean(pulse_data), distance=sampling_rate // 3
                )
                if len(peaks) > 0:
                    fig.add_trace(
                        go.Scatter(
                            x=time_axis[peaks],
                            y=np.array(pulse_data)[peaks],
                            mode="markers",
                            name="心跳峰值",
                            marker=dict(color="#F18F01", size=8, symbol="circle"),
                        )
                    )

                # 设置布局
                fig.update_layout(
                    title=config.title,
                    xaxis_title="时间 (秒)",
                    yaxis_title="幅度",
                    width=config.width,
                    height=config.height,
                    hovermode="x unified",
                    showlegend=config.show_legend,
                )

                # 添加网格
                if config.show_grid:
                    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="lightgray")
                    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="lightgray")

                html_content = fig.to_html(include_plotlyjs=True)

                return VisualizationResult(
                    chart_id=f"pulse_waveform_{int(datetime.now().timestamp())}",
                    chart_type=ChartType.WAVEFORM,
                    html_content=html_content,
                    interactive_data={"peaks": peaks.tolist(), "sampling_rate": sampling_rate},
                )

            else:
                # 创建静态图表
                fig, ax = plt.subplots(figsize=self.default_figsize)

                # 绘制波形
                ax.plot(time_axis, pulse_data, color="#2E86AB", linewidth=1.5, label="脉搏波形")

                # 检测并标记峰值
                peaks, _ = signal.find_peaks(
                    pulse_data, height=np.mean(pulse_data), distance=sampling_rate // 3
                )
                if len(peaks) > 0:
                    ax.scatter(
                        time_axis[peaks],
                        np.array(pulse_data)[peaks],
                        color="#F18F01",
                        s=50,
                        zorder=5,
                        label="心跳峰值",
                    )

                # 设置标题和标签
                ax.set_title(config.title, fontsize=16, fontweight="bold")
                ax.set_xlabel("时间 (秒)", fontsize=12)
                ax.set_ylabel("幅度", fontsize=12)

                if config.show_legend:
                    ax.legend()

                if config.show_grid:
                    ax.grid(True, alpha=0.3)

                # 保存为base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", dpi=self.default_dpi, bbox_inches="tight")
                buffer.seek(0)
                base64_image = base64.b64encode(buffer.getvalue()).decode()
                plt.close(fig)

                return VisualizationResult(
                    chart_id=f"pulse_waveform_{int(datetime.now().timestamp())}",
                    chart_type=ChartType.WAVEFORM,
                    base64_image=base64_image,
                )

        except Exception as e:
            logger.error(f"脉搏波形图创建失败: {e}")
            raise

    async def create_frequency_spectrum_chart(
        self, pulse_data: list[float], sampling_rate: int = 1000, config: ChartConfig | None = None
    ) -> VisualizationResult:
        """
        创建频谱分析图

        Args:
            pulse_data: 脉搏数据
            sampling_rate: 采样率
            config: 图表配置

        Returns:
            可视化结果
        """
        try:
            if config is None:
                config = ChartConfig(
                    chart_type=ChartType.SPECTRUM, title="脉搏频谱分析", width=800, height=600
                )

            # 计算FFT
            fft_values = fft(pulse_data)
            frequencies = fftfreq(len(pulse_data), 1 / sampling_rate)

            # 只取正频率部分
            positive_freq_idx = frequencies > 0
            frequencies = frequencies[positive_freq_idx]
            magnitude = np.abs(fft_values[positive_freq_idx])

            # 限制频率范围到0-10Hz（心率相关频率）
            freq_limit = 10
            freq_mask = frequencies <= freq_limit
            frequencies = frequencies[freq_mask]
            magnitude = magnitude[freq_mask]

            if config.interaction_mode == InteractionMode.INTERACTIVE:
                # 创建交互式频谱图
                fig = go.Figure()

                fig.add_trace(
                    go.Scatter(
                        x=frequencies,
                        y=magnitude,
                        mode="lines",
                        fill="tonexty",
                        name="频谱幅度",
                        line=dict(color="#A23B72", width=2),
                    )
                )

                # 标记主要频率峰值
                peak_indices, _ = signal.find_peaks(magnitude, height=np.max(magnitude) * 0.3)
                if len(peak_indices) > 0:
                    fig.add_trace(
                        go.Scatter(
                            x=frequencies[peak_indices],
                            y=magnitude[peak_indices],
                            mode="markers",
                            name="主要频率",
                            marker=dict(color="#F18F01", size=10, symbol="diamond"),
                        )
                    )

                fig.update_layout(
                    title=config.title,
                    xaxis_title="频率 (Hz)",
                    yaxis_title="幅度",
                    width=config.width,
                    height=config.height,
                    showlegend=config.show_legend,
                )

                html_content = fig.to_html(include_plotlyjs=True)

                return VisualizationResult(
                    chart_id=f"frequency_spectrum_{int(datetime.now().timestamp())}",
                    chart_type=ChartType.SPECTRUM,
                    html_content=html_content,
                )

            else:
                # 创建静态频谱图
                fig, ax = plt.subplots(figsize=self.default_figsize)

                ax.plot(frequencies, magnitude, color="#A23B72", linewidth=2)
                ax.fill_between(frequencies, magnitude, alpha=0.3, color="#A23B72")

                # 标记主要频率峰值
                peak_indices, _ = signal.find_peaks(magnitude, height=np.max(magnitude) * 0.3)
                if len(peak_indices) > 0:
                    ax.scatter(
                        frequencies[peak_indices],
                        magnitude[peak_indices],
                        color="#F18F01",
                        s=100,
                        zorder=5,
                        marker="D",
                        label="主要频率",
                    )

                ax.set_title(config.title, fontsize=16, fontweight="bold")
                ax.set_xlabel("频率 (Hz)", fontsize=12)
                ax.set_ylabel("幅度", fontsize=12)

                if config.show_legend and len(peak_indices) > 0:
                    ax.legend()

                if config.show_grid:
                    ax.grid(True, alpha=0.3)

                # 保存为base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", dpi=self.default_dpi, bbox_inches="tight")
                buffer.seek(0)
                base64_image = base64.b64encode(buffer.getvalue()).decode()
                plt.close(fig)

                return VisualizationResult(
                    chart_id=f"frequency_spectrum_{int(datetime.now().timestamp())}",
                    chart_type=ChartType.SPECTRUM,
                    base64_image=base64_image,
                )

        except Exception as e:
            logger.error(f"频谱分析图创建失败: {e}")
            raise

    async def create_constitution_radar_chart(
        self, constitution_scores: dict[str, float], config: ChartConfig | None = None
    ) -> VisualizationResult:
        """
        创建体质雷达图

        Args:
            constitution_scores: 体质评分字典
            config: 图表配置

        Returns:
            可视化结果
        """
        try:
            if config is None:
                config = ChartConfig(
                    chart_type=ChartType.RADAR, title="中医体质分析雷达图", width=600, height=600
                )

            # 体质类型中文名称映射
            constitution_names = {
                "balanced": "平和质",
                "qi_deficiency": "气虚质",
                "yang_deficiency": "阳虚质",
                "yin_deficiency": "阴虚质",
                "phlegm_dampness": "痰湿质",
                "damp_heat": "湿热质",
                "blood_stasis": "血瘀质",
                "qi_stagnation": "气郁质",
                "special": "特禀质",
            }

            # 准备数据
            categories = [constitution_names.get(k, k) for k in constitution_scores]
            values = list(constitution_scores.values())

            if config.interaction_mode == InteractionMode.INTERACTIVE:
                # 创建交互式雷达图
                fig = go.Figure()

                fig.add_trace(
                    go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill="toself",
                        name="体质评分",
                        line=dict(color="#2E86AB", width=3),
                        fillcolor="rgba(46, 134, 171, 0.3)",
                    )
                )

                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True, range=[0, 1], tickmode="linear", tick0=0, dtick=0.2
                        )
                    ),
                    title=config.title,
                    width=config.width,
                    height=config.height,
                    showlegend=config.show_legend,
                )

                html_content = fig.to_html(include_plotlyjs=True)

                return VisualizationResult(
                    chart_id=f"constitution_radar_{int(datetime.now().timestamp())}",
                    chart_type=ChartType.RADAR,
                    html_content=html_content,
                )

            else:
                # 创建静态雷达图
                fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection="polar"))

                # 计算角度
                angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)
                values_plot = values + [values[0]]  # 闭合图形
                angles_plot = np.concatenate((angles, [angles[0]]))

                # 绘制雷达图
                ax.plot(
                    angles_plot, values_plot, "o-", linewidth=3, color="#2E86AB", label="体质评分"
                )
                ax.fill(angles_plot, values_plot, alpha=0.25, color="#2E86AB")

                # 设置标签
                ax.set_xticks(angles)
                ax.set_xticklabels(categories, fontsize=10)
                ax.set_ylim(0, 1)
                ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
                ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=8)

                ax.set_title(config.title, size=16, fontweight="bold", pad=20)

                if config.show_legend:
                    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.0))

                if config.show_grid:
                    ax.grid(True, alpha=0.3)

                # 保存为base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", dpi=self.default_dpi, bbox_inches="tight")
                buffer.seek(0)
                base64_image = base64.b64encode(buffer.getvalue()).decode()
                plt.close(fig)

                return VisualizationResult(
                    chart_id=f"constitution_radar_{int(datetime.now().timestamp())}",
                    chart_type=ChartType.RADAR,
                    base64_image=base64_image,
                )

        except Exception as e:
            logger.error(f"体质雷达图创建失败: {e}")
            raise

    async def create_health_trend_chart(
        self, historical_data: list[dict[str, Any]], config: ChartConfig | None = None
    ) -> VisualizationResult:
        """
        创建健康趋势图

        Args:
            historical_data: 历史健康数据
            config: 图表配置

        Returns:
            可视化结果
        """
        try:
            if config is None:
                config = ChartConfig(
                    chart_type=ChartType.LINE, title="健康趋势分析", width=1000, height=600
                )

            # 准备数据
            df = pd.DataFrame(historical_data)
            if "timestamp" not in df.columns:
                df["timestamp"] = pd.date_range(end=datetime.now(), periods=len(df), freq="D")
            else:
                df["timestamp"] = pd.to_datetime(df["timestamp"])

            df = df.sort_values("timestamp")

            if config.interaction_mode == InteractionMode.INTERACTIVE:
                # 创建交互式趋势图
                fig = make_subplots(
                    rows=2,
                    cols=2,
                    subplot_titles=("整体健康评分", "心率变化", "血压趋势", "体质稳定性"),
                    specs=[
                        [{"secondary_y": False}, {"secondary_y": False}],
                        [{"secondary_y": True}, {"secondary_y": False}],
                    ],
                )

                # 整体健康评分
                if "overall_health" in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df["timestamp"],
                            y=df["overall_health"],
                            mode="lines+markers",
                            name="健康评分",
                            line=dict(color="#2E86AB", width=3),
                        ),
                        row=1,
                        col=1,
                    )

                # 心率变化
                if "heart_rate" in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df["timestamp"],
                            y=df["heart_rate"],
                            mode="lines+markers",
                            name="心率",
                            line=dict(color="#A23B72", width=2),
                        ),
                        row=1,
                        col=2,
                    )

                # 血压趋势
                if "systolic_bp" in df.columns and "diastolic_bp" in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df["timestamp"],
                            y=df["systolic_bp"],
                            mode="lines+markers",
                            name="收缩压",
                            line=dict(color="#F18F01", width=2),
                        ),
                        row=2,
                        col=1,
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=df["timestamp"],
                            y=df["diastolic_bp"],
                            mode="lines+markers",
                            name="舒张压",
                            line=dict(color="#C73E1D", width=2),
                        ),
                        row=2,
                        col=1,
                        secondary_y=True,
                    )

                # 体质稳定性
                if "constitution_stability" in df.columns:
                    fig.add_trace(
                        go.Bar(
                            x=df["timestamp"],
                            y=df["constitution_stability"],
                            name="体质稳定性",
                            marker_color="#6A994E",
                        ),
                        row=2,
                        col=2,
                    )

                fig.update_layout(
                    title=config.title,
                    width=config.width,
                    height=config.height,
                    showlegend=config.show_legend,
                )

                html_content = fig.to_html(include_plotlyjs=True)

                return VisualizationResult(
                    chart_id=f"health_trend_{int(datetime.now().timestamp())}",
                    chart_type=ChartType.LINE,
                    html_content=html_content,
                )

            else:
                # 创建静态趋势图
                fig, axes = plt.subplots(2, 2, figsize=(15, 10))
                fig.suptitle(config.title, fontsize=16, fontweight="bold")

                # 整体健康评分
                if "overall_health" in df.columns:
                    axes[0, 0].plot(
                        df["timestamp"],
                        df["overall_health"],
                        color="#2E86AB",
                        linewidth=3,
                        marker="o",
                        markersize=4,
                    )
                    axes[0, 0].set_title("整体健康评分")
                    axes[0, 0].set_ylabel("评分")
                    axes[0, 0].grid(True, alpha=0.3)

                # 心率变化
                if "heart_rate" in df.columns:
                    axes[0, 1].plot(
                        df["timestamp"],
                        df["heart_rate"],
                        color="#A23B72",
                        linewidth=2,
                        marker="s",
                        markersize=3,
                    )
                    axes[0, 1].set_title("心率变化")
                    axes[0, 1].set_ylabel("次/分钟")
                    axes[0, 1].grid(True, alpha=0.3)

                # 血压趋势
                if "systolic_bp" in df.columns and "diastolic_bp" in df.columns:
                    axes[1, 0].plot(
                        df["timestamp"],
                        df["systolic_bp"],
                        color="#F18F01",
                        linewidth=2,
                        marker="^",
                        markersize=3,
                        label="收缩压",
                    )
                    axes[1, 0].plot(
                        df["timestamp"],
                        df["diastolic_bp"],
                        color="#C73E1D",
                        linewidth=2,
                        marker="v",
                        markersize=3,
                        label="舒张压",
                    )
                    axes[1, 0].set_title("血压趋势")
                    axes[1, 0].set_ylabel("mmHg")
                    axes[1, 0].legend()
                    axes[1, 0].grid(True, alpha=0.3)

                # 体质稳定性
                if "constitution_stability" in df.columns:
                    axes[1, 1].bar(
                        df["timestamp"], df["constitution_stability"], color="#6A994E", alpha=0.7
                    )
                    axes[1, 1].set_title("体质稳定性")
                    axes[1, 1].set_ylabel("稳定性指数")
                    axes[1, 1].grid(True, alpha=0.3)

                # 调整布局
                plt.tight_layout()

                # 保存为base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", dpi=self.default_dpi, bbox_inches="tight")
                buffer.seek(0)
                base64_image = base64.b64encode(buffer.getvalue()).decode()
                plt.close(fig)

                return VisualizationResult(
                    chart_id=f"health_trend_{int(datetime.now().timestamp())}",
                    chart_type=ChartType.LINE,
                    base64_image=base64_image,
                )

        except Exception as e:
            logger.error(f"健康趋势图创建失败: {e}")
            raise

    async def create_risk_assessment_gauge(
        self, risk_scores: dict[str, float], config: ChartConfig | None = None
    ) -> VisualizationResult:
        """
        创建风险评估仪表盘

        Args:
            risk_scores: 风险评分字典
            config: 图表配置

        Returns:
            可视化结果
        """
        try:
            if config is None:
                config = ChartConfig(
                    chart_type=ChartType.GAUGE, title="健康风险评估仪表盘", width=800, height=600
                )

            if config.interaction_mode == InteractionMode.INTERACTIVE:
                # 创建交互式仪表盘
                fig = make_subplots(
                    rows=2,
                    cols=2,
                    specs=[
                        [{"type": "indicator"}, {"type": "indicator"}],
                        [{"type": "indicator"}, {"type": "indicator"}],
                    ],
                    subplot_titles=list(risk_scores.keys()),
                )

                positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
                colors = ["#2E86AB", "#A23B72", "#F18F01", "#6A994E"]

                for i, (risk_type, score) in enumerate(risk_scores.items()):
                    if i >= 4:  # 最多显示4个指标
                        break

                    # 确定颜色
                    if score < 0.3:
                        gauge_color = "green"
                    elif score < 0.6:
                        gauge_color = "yellow"
                    else:
                        gauge_color = "red"

                    fig.add_trace(
                        go.Indicator(
                            mode="gauge+number+delta",
                            value=score * 100,
                            domain={"x": [0, 1], "y": [0, 1]},
                            title={"text": risk_type},
                            delta={"reference": 50},
                            gauge={
                                "axis": {"range": [None, 100]},
                                "bar": {"color": colors[i]},
                                "steps": [
                                    {"range": [0, 30], "color": "lightgreen"},
                                    {"range": [30, 60], "color": "yellow"},
                                    {"range": [60, 100], "color": "lightcoral"},
                                ],
                                "threshold": {
                                    "line": {"color": "red", "width": 4},
                                    "thickness": 0.75,
                                    "value": 80,
                                },
                            },
                        ),
                        row=positions[i][0],
                        col=positions[i][1],
                    )

                fig.update_layout(title=config.title, width=config.width, height=config.height)

                html_content = fig.to_html(include_plotlyjs=True)

                return VisualizationResult(
                    chart_id=f"risk_gauge_{int(datetime.now().timestamp())}",
                    chart_type=ChartType.GAUGE,
                    html_content=html_content,
                )

            else:
                # 创建静态仪表盘
                n_gauges = len(risk_scores)
                cols = 2
                rows = (n_gauges + 1) // 2

                fig, axes = plt.subplots(rows, cols, figsize=(12, 6 * rows))
                if rows == 1:
                    axes = axes.reshape(1, -1)
                fig.suptitle(config.title, fontsize=16, fontweight="bold")

                for i, (risk_type, score) in enumerate(risk_scores.items()):
                    row = i // cols
                    col = i % cols
                    ax = axes[row, col]

                    # 创建半圆仪表盘
                    theta = np.linspace(0, np.pi, 100)

                    # 背景半圆
                    ax.plot(np.cos(theta), np.sin(theta), "lightgray", linewidth=20)

                    # 根据分数确定颜色
                    if score < 0.3:
                        color = "green"
                    elif score < 0.6:
                        color = "orange"
                    else:
                        color = "red"

                    # 分数对应的角度
                    score_theta = np.linspace(0, np.pi * score, int(100 * score))
                    ax.plot(np.cos(score_theta), np.sin(score_theta), color, linewidth=20)

                    # 添加指针
                    pointer_angle = np.pi * score
                    ax.arrow(
                        0,
                        0,
                        0.8 * np.cos(pointer_angle),
                        0.8 * np.sin(pointer_angle),
                        head_width=0.05,
                        head_length=0.05,
                        fc="black",
                        ec="black",
                    )

                    # 添加分数文本
                    ax.text(
                        0,
                        -0.3,
                        f"{score:.1%}",
                        ha="center",
                        va="center",
                        fontsize=16,
                        fontweight="bold",
                    )

                    # 设置标题
                    ax.set_title(risk_type, fontsize=14, fontweight="bold")

                    # 设置坐标轴
                    ax.set_xlim(-1.2, 1.2)
                    ax.set_ylim(-0.5, 1.2)
                    ax.set_aspect("equal")
                    ax.axis("off")

                # 隐藏多余的子图
                for i in range(n_gauges, rows * cols):
                    row = i // cols
                    col = i % cols
                    axes[row, col].axis("off")

                plt.tight_layout()

                # 保存为base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", dpi=self.default_dpi, bbox_inches="tight")
                buffer.seek(0)
                base64_image = base64.b64encode(buffer.getvalue()).decode()
                plt.close(fig)

                return VisualizationResult(
                    chart_id=f"risk_gauge_{int(datetime.now().timestamp())}",
                    chart_type=ChartType.GAUGE,
                    base64_image=base64_image,
                )

        except Exception as e:
            logger.error(f"风险评估仪表盘创建失败: {e}")
            raise

    async def create_correlation_heatmap(
        self, correlation_data: dict[str, dict[str, float]], config: ChartConfig | None = None
    ) -> VisualizationResult:
        """
        创建相关性热力图

        Args:
            correlation_data: 相关性数据
            config: 图表配置

        Returns:
            可视化结果
        """
        try:
            if config is None:
                config = ChartConfig(
                    chart_type=ChartType.HEATMAP, title="健康指标相关性分析", width=800, height=600
                )

            # 转换为DataFrame
            df = pd.DataFrame(correlation_data)

            if config.interaction_mode == InteractionMode.INTERACTIVE:
                # 创建交互式热力图
                fig = go.Figure(
                    data=go.Heatmap(
                        z=df.values,
                        x=df.columns,
                        y=df.index,
                        colorscale="RdBu",
                        zmid=0,
                        text=df.values,
                        texttemplate="%{text:.2f}",
                        textfont={"size": 10},
                        hoverongaps=False,
                    )
                )

                fig.update_layout(
                    title=config.title,
                    width=config.width,
                    height=config.height,
                    xaxis_title="健康指标",
                    yaxis_title="健康指标",
                )

                html_content = fig.to_html(include_plotlyjs=True)

                return VisualizationResult(
                    chart_id=f"correlation_heatmap_{int(datetime.now().timestamp())}",
                    chart_type=ChartType.HEATMAP,
                    html_content=html_content,
                )

            else:
                # 创建静态热力图
                fig, ax = plt.subplots(figsize=self.default_figsize)

                # 创建热力图
                im = ax.imshow(df.values, cmap="RdBu", aspect="auto", vmin=-1, vmax=1)

                # 设置标签
                ax.set_xticks(range(len(df.columns)))
                ax.set_yticks(range(len(df.index)))
                ax.set_xticklabels(df.columns, rotation=45, ha="right")
                ax.set_yticklabels(df.index)

                # 添加数值标注
                for i in range(len(df.index)):
                    for j in range(len(df.columns)):
                        text = ax.text(
                            j,
                            i,
                            f"{df.iloc[i, j]:.2f}",
                            ha="center",
                            va="center",
                            color="black",
                            fontsize=10,
                        )

                # 添加颜色条
                cbar = plt.colorbar(im, ax=ax)
                cbar.set_label("相关系数", rotation=270, labelpad=20)

                ax.set_title(config.title, fontsize=16, fontweight="bold")

                plt.tight_layout()

                # 保存为base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", dpi=self.default_dpi, bbox_inches="tight")
                buffer.seek(0)
                base64_image = base64.b64encode(buffer.getvalue()).decode()
                plt.close(fig)

                return VisualizationResult(
                    chart_id=f"correlation_heatmap_{int(datetime.now().timestamp())}",
                    chart_type=ChartType.HEATMAP,
                    base64_image=base64_image,
                )

        except Exception as e:
            logger.error(f"相关性热力图创建失败: {e}")
            raise

    async def create_real_time_monitor(
        self, data_stream_id: str, config: ChartConfig | None = None
    ) -> VisualizationResult:
        """
        创建实时监控图表

        Args:
            data_stream_id: 数据流ID
            config: 图表配置

        Returns:
            可视化结果
        """
        try:
            if config is None:
                config = ChartConfig(
                    chart_type=ChartType.LINE,
                    title="实时健康监控",
                    width=1200,
                    height=400,
                    interaction_mode=InteractionMode.REAL_TIME,
                )

            # 初始化实时数据缓存
            if data_stream_id not in self.real_time_data:
                self.real_time_data[data_stream_id] = {
                    "timestamps": [],
                    "values": [],
                    "max_points": 100,
                }

            # 创建实时图表HTML模板
            html_template = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <title>{config.title}</title>
            </head>
            <body>
                <div id="real-time-chart" style="width:{config.width}px;height:{config.height}px;"></div>
                
                <script>
                var data = [{{
                    x: [],
                    y: [],
                    mode: 'lines',
                    name: '实时数据',
                    line: {{color: '#2E86AB', width: 2}}
                }}];
                
                var layout = {{
                    title: '{config.title}',
                    xaxis: {{title: '时间'}},
                    yaxis: {{title: '数值'}},
                    showlegend: {str(config.show_legend).lower()}
                }};
                
                Plotly.newPlot('real-time-chart', data, layout);
                
                // 模拟实时数据更新
                function updateChart() {{
                    var now = new Date();
                    var value = Math.sin(now.getTime() / 1000) + Math.random() * 0.5;
                    
                    Plotly.extendTraces('real-time-chart', {{
                        x: [[now]],
                        y: [[value]]
                    }}, [0]);
                    
                    // 限制显示的数据点数量
                    if (data[0].x.length > 50) {{
                        Plotly.relayout('real-time-chart', {{
                            'xaxis.range': [data[0].x[data[0].x.length-50], data[0].x[data[0].x.length-1]]
                        }});
                    }}
                }}
                
                // 每{config.update_interval}毫秒更新一次
                setInterval(updateChart, {config.update_interval});
                </script>
            </body>
            </html>
            """

            return VisualizationResult(
                chart_id=f"real_time_monitor_{data_stream_id}",
                chart_type=ChartType.LINE,
                html_content=html_template,
                metadata={"data_stream_id": data_stream_id},
            )

        except Exception as e:
            logger.error(f"实时监控图表创建失败: {e}")
            raise

    async def create_comprehensive_dashboard(
        self, dashboard_data: dict[str, Any], config: ChartConfig | None = None
    ) -> VisualizationResult:
        """
        创建综合仪表板

        Args:
            dashboard_data: 仪表板数据
            config: 图表配置

        Returns:
            可视化结果
        """
        try:
            if config is None:
                config = ChartConfig(
                    chart_type=ChartType.LINE,  # 复合图表
                    title="健康管理综合仪表板",
                    width=1400,
                    height=1000,
                )

            # 创建子图
            fig = make_subplots(
                rows=3,
                cols=3,
                subplot_titles=[
                    "整体健康评分",
                    "脉搏波形",
                    "体质雷达图",
                    "风险评估",
                    "健康趋势",
                    "频谱分析",
                    "相关性分析",
                    "预测分析",
                    "建议摘要",
                ],
                specs=[
                    [{"type": "indicator"}, {"type": "scatter"}, {"type": "scatterpolar"}],
                    [{"type": "indicator"}, {"type": "scatter"}, {"type": "scatter"}],
                    [{"type": "heatmap"}, {"type": "scatter"}, {"type": "table"}],
                ],
            )

            # 1. 整体健康评分
            overall_score = dashboard_data.get("overall_score", 0.75)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=overall_score * 100,
                    title={"text": "健康评分"},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "bar": {"color": "#2E86AB"},
                        "steps": [
                            {"range": [0, 50], "color": "lightgray"},
                            {"range": [50, 80], "color": "yellow"},
                            {"range": [80, 100], "color": "green"},
                        ],
                    },
                ),
                row=1,
                col=1,
            )

            # 2. 脉搏波形
            pulse_data = dashboard_data.get("pulse_data", [])
            if pulse_data:
                time_axis = np.arange(len(pulse_data)) / 1000
                fig.add_trace(
                    go.Scatter(
                        x=time_axis,
                        y=pulse_data,
                        mode="lines",
                        name="脉搏",
                        line=dict(color="#A23B72"),
                    ),
                    row=1,
                    col=2,
                )

            # 3. 体质雷达图
            constitution_scores = dashboard_data.get("constitution_scores", {})
            if constitution_scores:
                categories = list(constitution_scores.keys())
                values = list(constitution_scores.values())
                fig.add_trace(
                    go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill="toself",
                        name="体质",
                        line=dict(color="#F18F01"),
                    ),
                    row=1,
                    col=3,
                )

            # 4. 风险评估
            risk_score = dashboard_data.get("risk_score", 0.3)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=risk_score * 100,
                    title={"text": "风险等级"},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "bar": {"color": "#C73E1D"},
                        "steps": [
                            {"range": [0, 30], "color": "green"},
                            {"range": [30, 60], "color": "yellow"},
                            {"range": [60, 100], "color": "red"},
                        ],
                    },
                ),
                row=2,
                col=1,
            )

            # 5. 健康趋势
            trend_data = dashboard_data.get("trend_data", [])
            if trend_data:
                dates = [datetime.now() - timedelta(days=i) for i in range(len(trend_data))]
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=trend_data,
                        mode="lines+markers",
                        name="趋势",
                        line=dict(color="#6A994E"),
                    ),
                    row=2,
                    col=2,
                )

            # 6. 频谱分析
            spectrum_data = dashboard_data.get("spectrum_data", {})
            if spectrum_data:
                frequencies = spectrum_data.get("frequencies", [])
                magnitudes = spectrum_data.get("magnitudes", [])
                fig.add_trace(
                    go.Scatter(
                        x=frequencies,
                        y=magnitudes,
                        mode="lines",
                        fill="tonexty",
                        name="频谱",
                        line=dict(color="#9B59B6"),
                    ),
                    row=2,
                    col=3,
                )

            # 7. 相关性分析
            correlation_matrix = dashboard_data.get("correlation_matrix", [[1, 0.5], [0.5, 1]])
            fig.add_trace(go.Heatmap(z=correlation_matrix, colorscale="RdBu", zmid=0), row=3, col=1)

            # 8. 预测分析
            prediction_data = dashboard_data.get("prediction_data", [])
            if prediction_data:
                future_dates = [
                    datetime.now() + timedelta(days=i) for i in range(len(prediction_data))
                ]
                fig.add_trace(
                    go.Scatter(
                        x=future_dates,
                        y=prediction_data,
                        mode="lines+markers",
                        name="预测",
                        line=dict(color="#E74C3C", dash="dash"),
                    ),
                    row=3,
                    col=2,
                )

            # 9. 建议摘要
            recommendations = dashboard_data.get("recommendations", ["保持良好习惯", "定期检查"])
            fig.add_trace(
                go.Table(header=dict(values=["健康建议"]), cells=dict(values=[recommendations])),
                row=3,
                col=3,
            )

            # 更新布局
            fig.update_layout(
                title=config.title, width=config.width, height=config.height, showlegend=False
            )

            html_content = fig.to_html(include_plotlyjs=True)

            return VisualizationResult(
                chart_id=f"comprehensive_dashboard_{int(datetime.now().timestamp())}",
                chart_type=ChartType.LINE,  # 复合图表
                html_content=html_content,
            )

        except Exception as e:
            logger.error(f"综合仪表板创建失败: {e}")
            raise

    def _get_color_scheme(self, style: VisualizationStyle) -> list[str]:
        """获取颜色方案"""
        return self.color_schemes.get(style, self.color_schemes[VisualizationStyle.MEDICAL])

    def _generate_gradient_colors(self, n_colors: int, base_color: str = "#2E86AB") -> list[str]:
        """生成渐变色"""
        colors = []
        for i in range(n_colors):
            # 转换为HSV
            rgb = tuple(int(base_color[j : j + 2], 16) for j in (1, 3, 5))
            hsv = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)

            # 调整色相
            new_hue = (hsv[0] + i * 0.1) % 1.0
            new_rgb = colorsys.hsv_to_rgb(new_hue, hsv[1], hsv[2])

            # 转换回十六进制
            hex_color = f"#{int(new_rgb[0] * 255):02x}{int(new_rgb[1] * 255):02x}{int(new_rgb[2] * 255):02x}"
            colors.append(hex_color)

        return colors

    async def update_real_time_data(self, data_stream_id: str, timestamp: datetime, value: float):
        """更新实时数据"""
        if data_stream_id in self.real_time_data:
            data = self.real_time_data[data_stream_id]
            data["timestamps"].append(timestamp)
            data["values"].append(value)

            # 限制数据点数量
            max_points = data["max_points"]
            if len(data["timestamps"]) > max_points:
                data["timestamps"] = data["timestamps"][-max_points:]
                data["values"] = data["values"][-max_points:]

    async def export_visualization(
        self, result: VisualizationResult, export_format: str = "png"
    ) -> str:
        """
        导出可视化结果

        Args:
            result: 可视化结果
            export_format: 导出格式 (png, html, svg, pdf)

        Returns:
            导出文件路径
        """
        try:
            filename = f"{result.chart_id}.{export_format}"
            filepath = Path(self.output_dir) / filename

            if export_format == "html" and result.html_content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(result.html_content)

            elif export_format == "png" and result.base64_image:
                import base64

                image_data = base64.b64decode(result.base64_image)
                with open(filepath, "wb") as f:
                    f.write(image_data)

            else:
                raise ValueError(f"不支持的导出格式或缺少相应数据: {export_format}")

            return str(filepath)

        except Exception as e:
            logger.error(f"可视化导出失败: {e}")
            raise

    def cleanup(self):
        """清理资源"""
        # 停止所有动画
        for animation_obj in self.animation_objects.values():
            if hasattr(animation_obj, "event_source"):
                animation_obj.event_source.stop()

        # 清理实时数据
        self.real_time_data.clear()
        self.animation_objects.clear()

        # 关闭线程池
        self.executor.shutdown(wait=True)

        logger.info("高级数据可视化器资源清理完成")
