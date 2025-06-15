# 索克生活 - 算诊服务 (Calculation Service)

## 项目概述

算诊服务是"索克生活"健康管理平台的核心微服务之一，专门提供传统中医算诊功能。该服务将中医"辨证论治未病"的理念数字化，为用户提供个性化的健康分析和调养建议。

## 核心功能

### 🔮 算诊分析功能
- **子午流注分析** - 基于十二经络时间规律的健康分析
- **八字体质分析** - 根据出生信息分析个人体质特征
- **八卦配属分析** - 基于八卦理论的健康配属分析
- **五运六气分析** - 当前时期和年度运气健康预测
- **综合算诊分析** - 整合多种算诊方法的全面分析

### 🛠️ 技术特性
- **异步处理** - 基于FastAPI的高性能异步API
- **智能缓存** - LRU缓存策略，提升响应速度
- **限流保护** - 滑动窗口限流算法，保障服务稳定
- **结构化日志** - 完整的请求/响应日志记录
- **错误处理** - 统一的异常处理和错误响应
- **健康检查** - 完善的服务健康监控

## 服务架构

```
calculation-service/
├── calculation_service/
│   ├── main.py                 # 服务入口
│   ├── config/
│   │   └── settings.py         # 配置管理
│   ├── api/
│   │   └── routes.py           # API路由
│   ├── core/
│   │   ├── config.py           # 核心配置
│   │   └── algorithms/         # 算法模块
│   │       ├── comprehensive_calculator.py
│   │       ├── ziwu_liuzhu/    # 子午流注
│   │       ├── constitution/   # 体质分析
│   │       ├── bagua/          # 八卦配属
│   │       └── wuyun_liuqi/    # 五运六气
│   ├── middleware/             # 中间件
│   │   ├── logging_middleware.py
│   │   ├── error_handler.py
│   │   └── rate_limiter.py
│   ├── utils/                  # 工具类
│   │   ├── cache.py
│   │   ├── formatters.py
│   │   ├── helpers.py
│   │   └── validators.py
│   └── exceptions/             # 异常定义
│       └── __init__.py
├── test_api.py                 # API测试脚本
└── README.md                   # 项目文档
```

## API 接口

### 服务信息
- `GET /` - 获取服务基本信息
- `GET /ping` - 服务ping检查
- `GET /api/v1/calculation/health` - 健康检查

### 算诊分析
- `POST /api/v1/calculation/comprehensive` - 综合算诊分析
- `GET /api/v1/calculation/ziwu-liuzhu` - 子午流注分析
- `POST /api/v1/calculation/constitution` - 体质分析
- `POST /api/v1/calculation/bagua` - 八卦配属分析
- `GET /api/v1/calculation/wuyun-liuqi/current` - 当前运气分析
- `GET /api/v1/calculation/wuyun-liuqi/yearly/{year}` - 年度运气预测
- `GET /api/v1/calculation/health-advice` - 健康建议

### 缓存管理
- `GET /cache/stats` - 缓存统计信息
- `POST /cache/clear` - 清空缓存

## 快速开始

### 环境要求
- Python 3.13.3+
- FastAPI
- Uvicorn
- Pydantic

### 安装依赖
```bash
pip install fastapi uvicorn pydantic pydantic-settings requests
```

### 启动服务
```bash
# 开发模式启动
python -m calculation_service.main

# 后台运行
python -m calculation_service.main &
```

服务将在 `http://localhost:8003` 启动

### API 文档
启动服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc

### 测试服务
```bash
# 运行完整测试
python test_api.py

# 手动测试示例
curl -X POST "http://localhost:8003/api/v1/calculation/comprehensive" \
  -H "Content-Type: application/json" \
  -d '{
    "personal_info": {
      "birth_year": 1990,
      "birth_month": 5,
      "birth_day": 15,
      "birth_hour": 14,
      "gender": "男"
    },
    "analysis_date": "2024-01-15"
  }'
```

## 配置说明

### 服务配置 (config/settings.py)
- `SERVICE_NAME`: 服务名称
- `SERVICE_VERSION`: 服务版本
- `HOST`: 服务主机地址
- `PORT`: 服务端口
- `DEBUG`: 调试模式

### 缓存配置
- `CACHE_MAX_SIZE`: 缓存最大容量 (默认: 1000)
- `CACHE_DEFAULT_TTL`: 默认缓存时间 (默认: 3600秒)

### 限流配置
- `RATE_LIMIT_REQUESTS`: 限流请求数 (默认: 100)
- `RATE_LIMIT_WINDOW`: 限流时间窗口 (默认: 60秒)

## 算法说明

### 子午流注算法
基于中医十二经络的时间规律，分析最佳治疗和养生时机：
- 子时(23-1点): 胆经当令
- 丑时(1-3点): 肝经当令
- 寅时(3-5点): 肺经当令
- ... (完整十二时辰循环)

### 体质分析算法
根据出生信息分析个人体质类型：
- 平和质、气虚质、阳虚质
- 阴虚质、痰湿质、湿热质
- 血瘀质、气郁质、特禀质

### 八卦配属算法
基于八卦理论分析个人健康配属：
- 乾卦(金): 头部、心脑血管
- 坤卦(土): 脾胃、消化系统
- 震卦(木): 肝胆、神经系统
- ... (完整八卦对应)

### 五运六气算法
分析当前时期的运气特点：
- 五运: 木运、火运、土运、金运、水运
- 六气: 风木、君火、相火、湿土、燥金、寒水

## 监控与日志

### 日志级别
- `INFO`: 正常操作日志
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `DEBUG`: 调试信息

### 监控指标
- 请求响应时间
- 错误率统计
- 缓存命中率
- 限流触发次数

## 部署说明

### Docker 部署
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8003
CMD ["python", "-m", "calculation_service.main"]
```

### 生产环境配置
- 使用 Gunicorn + Uvicorn 部署
- 配置反向代理 (Nginx)
- 设置环境变量
- 配置日志轮转

## 开发指南

### 代码规范
- 遵循 PEP 8 代码风格
- 使用类型注解
- 编写完整的文档字符串
- 单元测试覆盖率 > 80%

### 添加新算法
1. 在 `core/algorithms/` 下创建新模块
2. 实现算法计算器类
3. 在 `api/routes.py` 中添加路由
4. 更新测试用例

## 故障排除

### 常见问题
1. **服务启动失败**: 检查端口占用和依赖安装
2. **API 响应慢**: 检查缓存配置和数据库连接
3. **内存占用高**: 调整缓存大小和清理策略

### 日志查看
```bash
# 查看服务日志
tail -f logs/calculation-service.log

# 查看错误日志
grep ERROR logs/calculation-service.log
```

## 版本历史

### v1.0.0 (2024-01-15)
- ✅ 完成基础服务架构
- ✅ 实现五大算诊功能
- ✅ 添加缓存和限流机制
- ✅ 完善错误处理和日志
- ✅ 提供完整API文档

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码变更
4. 编写测试用例
5. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目维护者: 索克生活开发团队
- 邮箱: dev@suoke.life
- 文档: https://docs.suoke.life

---

**索克生活 - 让传统中医智慧融入现代生活** 🌿 