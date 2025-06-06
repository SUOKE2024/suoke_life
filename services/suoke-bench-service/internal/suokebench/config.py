"""
config - 索克生活项目模块
"""

from pathlib import Path
from pydantic import BaseModel, model_validator
import os
import yaml

"""
配置加载与管理模块
"""




class DatasetConfig(BaseModel):
    """数据集配置"""

    name: str
    path: str
    type: str
    format: str
    size: int
    description: str
    tags: list[str] = []
    metadata: dict[str, str] = {}


class MetricConfig(BaseModel):
    """评测指标配置"""

    name: str
    type: str
    description: str
    threshold: float
    unit: str = ""
    higher_is_better: bool = True
    weight: float = 1.0
    aggregation: str = "mean"


class TaskConfig(BaseModel):
    """任务配置"""

    id: str
    name: str
    type: str
    description: str
    datasets: list[str]
    metrics: list[str]
    parameters: dict[str, str] = {}
    timeout_seconds: int = 3600
    tags: list[str] = []
    priority: int = 5


class ReportConfig(BaseModel):
    """报告配置"""

    template_dir: str
    output_dir: str
    default_format: str = "html"
    include_plots: bool = True
    logo_path: str | None = None
    title_prefix: str = "SuokeBench评测报告"


class BenchConfig(BaseModel):
    """总体配置"""

    service_name: str
    version: str
    data_root: str
    datasets: dict[str, DatasetConfig]
    metrics: dict[str, MetricConfig]
    tasks: dict[str, TaskConfig]
    report: ReportConfig
    cache_dir: str
    max_workers: int = 4
    log_level: str = "INFO"

    @model_validator(mode="after")
    def validate_paths(self) -> "BenchConfig":
        """验证所有路径"""
        # 确保数据根目录存在
        data_root = Path(self.data_root)
        if not data_root.exists():
            data_root.mkdir(parents=True, exist_ok=True)

        # 确保缓存目录存在
        cache_dir = Path(self.cache_dir)
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)

        # 确保报告目录存在
        report_dir = Path(self.report.output_dir)
        if not report_dir.exists():
            report_dir.mkdir(parents=True, exist_ok=True)

        return self


def load_config(config_path: str) -> BenchConfig:
    """
    加载配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        解析后的配置对象
    """
    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        # 如果不存在，使用默认配置
        return create_default_config()

    # 从YAML文件加载配置
    with open(config_path, encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    # 解析配置
    return BenchConfig(**config_data)


def create_default_config() -> BenchConfig:
    """
    创建默认配置

    Returns:
        默认配置对象
    """
    # 创建基本目录
    data_root = os.path.abspath("./data")
    cache_dir = os.path.abspath("./cache")
    report_output_dir = os.path.abspath("./reports")

    for directory in [data_root, cache_dir, report_output_dir]:
        os.makedirs(directory, exist_ok=True)

    # 构建默认配置
    default_config = {
        "service_name": "suoke-bench-service",
        "version": "0.1.0",
        "data_root": data_root,
        "cache_dir": cache_dir,
        "max_workers": 4,
        "log_level": "INFO",
        "datasets": {
            "tcm_4d_sample": {
                "name": "中医五诊样例数据集",
                "path": f"{data_root}/tcm_4d_sample",
                "type": "multimodal",
                "format": "mixed",
                "size": 100,
                "description": "中医五诊数据集样例",
                "tags": ["中医", "五诊", "样例"],
            },
            "health_plan_sample": {
                "name": "健康方案样例数据集",
                "path": f"{data_root}/health_plan_sample",
                "type": "text",
                "format": "json",
                "size": 50,
                "description": "健康方案生成样例",
                "tags": ["健康方案", "样例"],
            },
        },
        "metrics": {
            "accuracy": {
                "name": "准确率",
                "type": "classification",
                "description": "分类准确率",
                "threshold": 0.8,
                "unit": "%",
                "higher_is_better": True,
            },
            "f1": {
                "name": "F1分数",
                "type": "classification",
                "description": "F1分数",
                "threshold": 0.75,
                "unit": "",
                "higher_is_better": True,
            },
            "rouge_l": {
                "name": "ROUGE-L",
                "type": "generation",
                "description": "ROUGE-L评分",
                "threshold": 0.6,
                "unit": "",
                "higher_is_better": True,
            },
            "latency_p95": {
                "name": "P95延迟",
                "type": "performance",
                "description": "95%的请求延迟",
                "threshold": 500,
                "unit": "ms",
                "higher_is_better": False,
            },
        },
        "tasks": {
            "tongue_recognition": {
                "id": "tongue_recognition",
                "name": "舌象识别",
                "type": "TCM_DIAGNOSIS",
                "description": "识别舌象特征",
                "datasets": ["tcm_4d_sample"],
                "metrics": ["accuracy", "f1"],
                "parameters": {"min_confidence": "0.7"},
            },
            "health_plan_gen": {
                "id": "health_plan_gen",
                "name": "健康方案生成",
                "type": "HEALTH_PLAN_GENERATION",
                "description": "生成个性化健康方案",
                "datasets": ["health_plan_sample"],
                "metrics": ["rouge_l"],
                "parameters": {},
            },
        },
        "report": {
            "template_dir": "./templates",
            "output_dir": report_output_dir,
            "default_format": "html",
            "include_plots": True,
            "title_prefix": "SuokeBench评测报告",
        },
    }

    return BenchConfig(**default_config)
