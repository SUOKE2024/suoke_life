"""
SuokeBench 评测环境设置
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

from internal.suokebench.config import BenchConfig, load_config

logger = logging.getLogger(__name__)


class BenchSetup:
    """评测环境设置"""
    
    def __init__(self, config_path: str = None):
        """
        初始化设置
        
        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config = load_config(config_path or "config/config.yaml")
        
        # 设置日志
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )
        
    def setup(self):
        """设置评测环境"""
        logger.info("开始设置SuokeBench评测环境")
        
        # 检查并创建必要的目录
        self._ensure_directories()
        
        # 检测GPU可用性
        gpus = self._detect_gpus()
        if gpus:
            logger.info(f"检测到 {len(gpus)} 个可用GPU: {', '.join(gpus)}")
        else:
            logger.info("未检测到可用GPU，将使用CPU运行评测")
            
        # 下载示例数据集
        self._download_sample_datasets()
        
        # 创建报告模板目录
        self._create_report_templates()
        
        logger.info("SuokeBench评测环境设置完成")
        
    def _ensure_directories(self):
        """确保必要的目录存在"""
        # 数据根目录
        data_root = Path(self.config.data_root)
        data_root.mkdir(parents=True, exist_ok=True)
        logger.info(f"确保数据根目录存在: {data_root}")
        
        # 缓存目录
        cache_dir = Path(self.config.cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"确保缓存目录存在: {cache_dir}")
        
        # 报告输出目录
        report_dir = Path(self.config.report.output_dir)
        report_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"确保报告输出目录存在: {report_dir}")
        
        # 模板目录
        template_dir = Path(self.config.report.template_dir)
        template_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"确保模板目录存在: {template_dir}")
        
        # 为每个数据集创建目录
        for dataset_id, dataset in self.config.datasets.items():
            dataset_dir = Path(dataset.path)
            dataset_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"确保数据集目录存在: {dataset_dir}")
        
    def _detect_gpus(self) -> List[str]:
        """
        检测可用的GPU
        
        Returns:
            GPU列表，如果没有则为空列表
        """
        # 尝试使用PyTorch检测GPU
        try:
            import torch
            if torch.cuda.is_available():
                return [f"cuda:{i} ({torch.cuda.get_device_name(i)})" for i in range(torch.cuda.device_count())]
        except ImportError:
            logger.warning("无法导入PyTorch，将尝试使用其他方法检测GPU")
            
        # 尝试使用TensorFlow检测GPU
        try:
            import tensorflow as tf
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                return [str(gpu) for gpu in gpus]
        except ImportError:
            logger.warning("无法导入TensorFlow，将尝试使用系统命令检测GPU")
            
        # 尝试使用系统命令检测GPU
        try:
            import subprocess
            
            # NVIDIA GPU
            try:
                output = subprocess.check_output(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'])
                return output.decode('utf-8').strip().split('\n')
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
                
            # AMD GPU on Linux
            try:
                output = subprocess.check_output(['rocm-smi', '--showproductname'])
                return [line.split(':')[1].strip() for line in output.decode('utf-8').strip().split('\n') if ':' in line]
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
                
        except Exception as e:
            logger.warning(f"使用系统命令检测GPU失败: {str(e)}")
            
        # 如果所有方法都失败，返回空列表
        return []
        
    def _download_sample_datasets(self):
        """下载示例数据集"""
        # 为简化实现，这里只创建示例数据的目录结构
        # 实际项目中应下载或生成真实数据
        
        for dataset_id, dataset in self.config.datasets.items():
            dataset_dir = Path(dataset.path)
            
            # 创建示例数据文件
            sample_file = dataset_dir / "sample.json"
            
            if not sample_file.exists():
                logger.info(f"创建示例数据文件: {sample_file}")
                with open(sample_file, "w", encoding="utf-8") as f:
                    f.write('{"samples": [{"id": "sample_1", "input": "示例输入", "expected": "示例输出"}]}')
                    
            # 创建数据集描述文件
            dataset_card = dataset_dir / "dataset_card.md"
            
            if not dataset_card.exists():
                logger.info(f"创建数据集描述文件: {dataset_card}")
                with open(dataset_card, "w", encoding="utf-8") as f:
                    f.write(f"""# {dataset.name}

## 概述

- **类型**: {dataset.type}
- **格式**: {dataset.format}
- **大小**: {dataset.size} 个样本
- **标签**: {', '.join(dataset.tags)}

## 描述

{dataset.description}

## 样本结构

```json
{{
  "id": "sample_id",
  "input": "示例输入",
  "expected": "示例输出"
}}
```

## 版权与伦理声明

本数据集仅用于评测目的，所有数据均已进行脱敏处理。
""")
        
    def _create_report_templates(self):
        """创建报告模板"""
        template_dir = Path(self.config.report.template_dir)
        
        # HTML模板
        html_template = template_dir / "report.html"
        
        if not html_template.exists():
            logger.info(f"创建HTML报告模板: {html_template}")
            with open(html_template, "w", encoding="utf-8") as f:
                f.write("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3 {
            color: #35BB78;
        }
        .header {
            display: flex;
            align-items: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #35BB78;
            padding-bottom: 10px;
        }
        .header img {
            height: 60px;
            margin-right: 20px;
        }
        .summary {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #35BB78;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .plot-container {
            margin: 20px 0;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 0.9em;
            color: #777;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="{{ config.logo_path|default('logo.png') }}" alt="索克生活">
        <div>
            <h1>{{ title }}</h1>
            <p>生成时间: {{ timestamp }}</p>
        </div>
    </div>

    <section class="summary">
        <h2>评测摘要</h2>
        <p>运行ID: {{ run_id }}</p>
        <p>服务版本: {{ config.version }}</p>
        <p>总任务数: {{ summary.tasks }}</p>
        <p>成功任务: {{ summary.success }}</p>
        <p>失败任务: {{ summary.failed }}</p>
        <p>成功率: {{ (summary.success / summary.tasks * 100)|round(2) }}%</p>
    </section>

    <section>
        <h2>指标摘要</h2>
        {% if metrics_summary.metrics %}
        <table>
            <tr>
                <th>指标</th>
                <th>平均值</th>
                <th>最小值</th>
                <th>最大值</th>
            </tr>
            {% for metric_name, metric_data in metrics_summary.metrics.items() %}
            <tr>
                <td>{{ metric_name }}</td>
                <td>{{ metric_data.avg|round(4) }}</td>
                <td>{{ metric_data.min|round(4) }}</td>
                <td>{{ metric_data.max|round(4) }}</td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p>没有可用的指标数据</p>
        {% endif %}
    </section>

    {% if plots %}
    <section>
        <h2>可视化分析</h2>
        
        {% if plots.overall_metrics %}
        <div class="plot-container">
            <h3>总体指标</h3>
            {{ plots.overall_metrics|safe }}
        </div>
        {% endif %}
        
        {% if plots.task_success_rate %}
        <div class="plot-container">
            <h3>任务成功率</h3>
            {{ plots.task_success_rate|safe }}
        </div>
        {% endif %}
    </section>
    {% endif %}

    <section>
        <h2>任务详情</h2>
        {% for task_id, result in summary.results.items() %}
        <h3>{{ task_id }}</h3>
        <table>
            <tr>
                <th>状态</th>
                <td>{{ result.status }}</td>
            </tr>
            {% if result.status == "SUCCESS" %}
            <tr>
                <th>处理样本数</th>
                <td>{{ result.samples_processed|default("未知") }}</td>
            </tr>
            <tr>
                <th>运行时间</th>
                <td>{{ result.duration_seconds|default("未知") }} 秒</td>
            </tr>
            {% if result.metrics %}
            <tr>
                <th>指标</th>
                <td>
                    <ul>
                    {% for metric_name, metric_value in result.metrics.items() %}
                        <li>{{ metric_name }}: {{ metric_value }}</li>
                    {% endfor %}
                    </ul>
                </td>
            </tr>
            {% endif %}
            {% else %}
            <tr>
                <th>错误信息</th>
                <td>{{ result.error|default("未知错误") }}</td>
            </tr>
            {% endif %}
        </table>
        {% endfor %}
    </section>

    <div class="footer">
        <p>© {{ timestamp[:4] }} 索克生活. SuokeBench评测报告</p>
    </div>
</body>
</html>""")
                
        # Markdown模板
        md_template = template_dir / "report.md"
        
        if not md_template.exists():
            logger.info(f"创建Markdown报告模板: {md_template}")
            with open(md_template, "w", encoding="utf-8") as f:
                f.write("""# {{ title }}

生成时间: {{ timestamp }}

## 评测摘要

- 运行ID: {{ run_id }}
- 服务版本: {{ config.version }}
- 总任务数: {{ summary.tasks }}
- 成功任务: {{ summary.success }}
- 失败任务: {{ summary.failed }}
- 成功率: {{ (summary.success / summary.tasks * 100)|round(2) }}%

## 指标摘要

{% if metrics_summary.metrics %}
| 指标 | 平均值 | 最小值 | 最大值 |
|------|--------|--------|--------|
{% for metric_name, metric_data in metrics_summary.metrics.items() %}
| {{ metric_name }} | {{ metric_data.avg|round(4) }} | {{ metric_data.min|round(4) }} | {{ metric_data.max|round(4) }} |
{% endfor %}
{% else %}
没有可用的指标数据
{% endif %}

## 任务详情

{% for task_id, result in summary.results.items() %}
### {{ task_id }}

- 状态: {{ result.status }}
{% if result.status == "SUCCESS" %}
- 处理样本数: {{ result.samples_processed|default("未知") }}
- 运行时间: {{ result.duration_seconds|default("未知") }} 秒
{% if result.metrics %}
- 指标:
{% for metric_name, metric_value in result.metrics.items() %}
  - {{ metric_name }}: {{ metric_value }}
{% endfor %}
{% endif %}
{% else %}
- 错误信息: {{ result.error|default("未知错误") }}
{% endif %}

{% endfor %}

---

© {{ timestamp[:4] }} 索克生活. SuokeBench评测报告""")


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="SuokeBench评测环境设置")
    parser.add_argument("--config", type=str, help="配置文件路径")
    args = parser.parse_args()
    
    # 创建并运行设置
    setup = BenchSetup(args.config)
    setup.setup()


if __name__ == "__main__":
    main()