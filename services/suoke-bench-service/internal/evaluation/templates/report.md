# {{ title }}

*生成时间: {{ timestamp }}*

## 测试概述

| 项目 | 值 | 项目 | 值 |
|-----|-----|-----|-----|
| **运行ID** | {{ run_id }} | **基准测试** | {{ benchmark_id }} |
| **模型** | {{ model_id }} | **版本** | {{ model_version }} |
| **状态** | {{ status }} | **通过率** | {{ "%.2f%%" | format(passing_rate * 100) }} |
| **开始时间** | {{ created_at }} | **完成时间** | {{ completed_at }} |

## 总结

{{ summary }}

## 性能指标

{% for metric in metrics %}
### {{ metric.display_name }} ({{ "%.2f" | format(metric.value) }}{{ metric.unit }})

- **状态**: {{ "✅ 通过" if metric.pass else "❌ 未通过" }}
- **阈值**: {{ "%.2f" | format(metric.threshold) }}{{ metric.unit }}
{% if metric.comparison %}
- **比较**: {{ metric.comparison }}
{% endif %}

{% endfor %}

{% if samples %}
## 样本结果分析

**样本统计**:
- 总样本数: {{ samples|length }}
- 正确样本数: {{ samples|selectattr('correct', 'eq', true)|list|length }}
- 错误样本数: {{ samples|selectattr('correct', 'eq', false)|list|length }}
- 正确率: {{ "%.2f%%" | format(100 * samples|selectattr('correct', 'eq', true)|list|length / samples|length) }}

**样本详情**:

{% for sample in samples %}
### 样本 {{ sample.id }} ({{ "✅ 正确" if sample.correct else "❌ 错误" }})

**输入**:
```
{{ sample.input }}
```

**期望输出**:
```
{{ sample.expected }}
```

**实际输出**:
```
{{ sample.actual }}
```

{% endfor %}
{% endif %}

---

*由 SuokeBench 评测系统生成* 