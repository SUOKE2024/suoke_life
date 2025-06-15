# 无障碍服务快速启动指南

## 🚀 快速开始

### 1. 环境要求
- Python 3.13.3+
- UV 包管理器
- 8GB+ 内存
- 2GB+ 磁盘空间

### 2. 安装依赖
```bash
# 进入服务目录
cd services/accessibility-service

# 安装基础依赖
pip install grpcio grpcio-tools pyyaml psutil aiohttp

# 或使用 UV (推荐)
uv add grpcio grpcio-tools pyyaml psutil aiohttp
```

### 3. 快速验证
```bash
# 运行快速验证
python quick_validation.py

# 运行综合演示
python demo_comprehensive.py
```

## 📊 核心功能演示

### 健康检查系统
```bash
# 测试基础健康检查
python -c "
import asyncio
from internal.service.health_check import global_health_manager, setup_default_health_checks
from config.config import Config

async def test():
    setup_default_health_checks(Config())
    health = await global_health_manager.check_health()
    print(f'健康状态: {health.overall_status.value}')
    print(f'检查项目: {len(health.checks)}')

asyncio.run(test())
"
```

### 高级监控演示
```bash
# 测试高级健康检查和告警
python test_advanced_health.py
```

### 性能告警演示
```bash
# 测试性能告警系统
python test_performance_alerting.py
```

## 🔧 配置说明

### 基础配置 (config/config.yaml)
```yaml
# 服务基础配置
service:
  name: "accessibility-service"
  version: "1.0.0"
  port: 8080

# 健康检查配置
health_check:
  interval: 60  # 检查间隔(秒)
  timeout: 5    # 超时时间(秒)

# 性能监控配置
performance:
  metrics_retention: 1000  # 指标保留数量
  alert_cooldown: 300     # 告警冷却时间(秒)
```

### 告警阈值配置
```python
# 在代码中自定义阈值
from internal.service.performance_alerting import ThresholdRule, ThresholdType, AlertLevel

# CPU 使用率阈值
cpu_rule = ThresholdRule(
    name="high_cpu",
    metric_name="cpu_percent",
    threshold_type=ThresholdType.STATIC,
    alert_level=AlertLevel.WARNING,
    value=80.0,
    comparison=">",
    duration_seconds=300
)
```

## 📈 监控指标

### 系统指标
- **CPU使用率**: `cpu_percent`
- **内存使用率**: `memory_percent`
- **磁盘使用率**: `disk_usage`
- **网络连接**: `network_connectivity`

### 应用指标
- **响应时间**: `response_time`
- **错误率**: `error_rate`
- **请求数量**: `request_count`
- **活跃连接**: `active_connections`

### 自定义指标
```python
from internal.service.performance_alerting import record_performance_metric, MetricType

# 记录自定义指标
record_performance_metric("custom_metric", 100.0, metric_type=MetricType.GAUGE)
```

## 🚨 告警配置

### 默认告警规则
1. **系统不健康**: 任何健康检查失败
2. **多个性能问题**: 2个以上性能指标异常
3. **高故障率**: 健康检查失败率 > 50%
4. **CPU使用率过高**: > 80% 持续5分钟
5. **内存使用率过高**: > 90% 持续3分钟

### 自定义告警处理器
```python
async def custom_alert_handler(alert):
    """自定义告警处理器"""
    print(f"自定义告警: {alert.message}")
    # 发送到外部系统
    # await send_to_external_system(alert)

# 注册处理器
from internal.service.advanced_health_check import global_alert_manager
global_alert_manager.add_notification_handler(custom_alert_handler)
```

## 🛠️ 故障排除

### 常见问题

#### 1. 导入错误
```bash
# 确保在正确目录
cd services/accessibility-service

# 检查 Python 路径
python -c "import sys; print(sys.path)"
```

#### 2. 依赖缺失
```bash
# 安装缺失依赖
pip install grpcio grpcio-tools pyyaml psutil aiohttp

# 检查依赖版本
pip list | grep -E "(grpcio|pyyaml|psutil|aiohttp)"
```

#### 3. 权限问题
```bash
# 检查文件权限
ls -la config/
ls -la internal/service/

# 修复权限
chmod +r config/*.yaml
chmod +x *.py
```

#### 4. 网络检查失败
```bash
# 测试网络连接
curl -I https://www.baidu.com
curl -I https://httpbin.org/status/200

# 检查防火墙设置
```

### 调试模式
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 运行调试版本
python -c "
import asyncio
from demo_comprehensive import ComprehensiveDemo

async def debug_run():
    demo = ComprehensiveDemo()
    await demo.initialize_systems()
    print('调试模式启动成功')

asyncio.run(debug_run())
"
```

## 📊 性能优化

### 1. 减少检查频率
```python
# 调整健康检查间隔
from internal.service.health_check import global_health_manager
# 设置更长的检查间隔
```

### 2. 限制历史数据
```python
# 减少指标历史保留
from internal.service.performance_alerting import global_performance_threshold_manager
# 调整 history_size 参数
```

### 3. 优化网络检查
```python
# 减少网络端点数量
from internal.service.advanced_health_check import NetworkHealthChecker
# 只检查关键端点
```

## 🔍 监控最佳实践

### 1. 分层监控
- **基础层**: 系统资源监控
- **应用层**: 服务健康监控
- **业务层**: 关键指标监控

### 2. 告警策略
- **分级告警**: INFO < WARNING < CRITICAL < EMERGENCY
- **告警聚合**: 避免告警风暴
- **自动恢复**: 问题解决后自动清除告警

### 3. 性能调优
- **合理阈值**: 基于历史数据设置
- **趋势分析**: 关注长期趋势变化
- **容量规划**: 提前预测资源需求

## 📞 技术支持

### 文档资源
- `README.md` - 项目概述
- `MIDTERM_IMPROVEMENT_REPORT.md` - 中期改进报告
- `FINAL_PROJECT_SUMMARY.md` - 项目总结报告

### 测试文件
- `quick_validation.py` - 快速验证
- `test_advanced_health.py` - 高级健康检查测试
- `test_performance_alerting.py` - 性能告警测试
- `demo_comprehensive.py` - 综合功能演示

### 联系方式
- 项目仓库: `/Users/songxu/Developer/suoke_life`
- 服务目录: `services/accessibility-service`

---

**快速启动指南版本**: 1.0  
**最后更新**: 2024年12月19日  
**适用版本**: Python 3.13.3+ 🐍 