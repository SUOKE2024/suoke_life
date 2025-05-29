# 算诊微服务 (Calculation Service)

## 概述

算诊微服务是索克生活平台中的第五诊断方法，基于传统中医"算"诊理论，融合易学、天文历法等传统文化智慧，为用户提供基于时间、空间、个体体质的综合诊断分析。

## 理论基础

### 历史渊源

1. **《内经》中的"术数"思想**
   - 《素问·五运行大论》："候之所始，道之所生"
   - 《灵枢·九宫八风》：以"九宫八卦"对应人体部位

2. **道家与医家的结合**
   - 孙思邈《千金方》："凡欲为大医，须妙解阴阳禄命"
   - 明代《医宗金鉴》收录"运气学说"

3. **民间传承**
   - 道医、苗医等保留的"问卦定病""择时针灸"传统

### 核心方法

1. **五运六气推演**
   - 根据患者出生年月日及发病时间推算体质偏性
   - 应用干支纪年推算当年易发疾病

2. **八卦/奇门遁甲配属**
   - 将人体脏腑对应八卦方位
   - 通过卦象变化判断病位

3. **子午流注与灵龟八法**
   - 按时辰推算气血流注经络
   - 选择最佳针灸时间

4. **命理体质学**
   - 通过八字五行强弱判断体质倾向
   - 指导个性化养生方案

## 技术架构

### 核心模块

```
calculation_service/
├── api/                    # API接口层
│   ├── v1/                # API版本1
│   │   ├── calculation/   # 算诊计算接口
│   │   ├── calendar/      # 历法计算接口
│   │   └── constitution/  # 体质分析接口
│   └── middleware/        # 中间件
├── core/                  # 核心业务逻辑
│   ├── algorithms/        # 算诊算法
│   │   ├── wuyun_liuqi/  # 五运六气
│   │   ├── bagua/        # 八卦推演
│   │   ├── ziwu_liuzhu/  # 子午流注
│   │   └── constitution/ # 体质分析
│   ├── calendar/         # 历法计算
│   │   ├── lunar/        # 农历计算
│   │   ├── solar/        # 阳历计算
│   │   └── astronomical/ # 天文计算
│   └── models/           # 数据模型
├── data/                 # 数据层
│   ├── repositories/     # 数据仓库
│   └── schemas/          # 数据模式
├── services/             # 服务层
│   ├── calculation/      # 计算服务
│   ├── analysis/         # 分析服务
│   └── recommendation/   # 推荐服务
└── utils/                # 工具类
    ├── validators/       # 验证器
    └── formatters/       # 格式化器
```

### 技术栈

- **Python 3.13.3**: 最新Python版本
- **UV**: 现代Python包管理器
- **FastAPI**: 高性能Web框架
- **Pydantic**: 数据验证和序列化
- **NumPy/SciPy**: 科学计算
- **Pandas**: 数据分析
- **LunarDate**: 农历计算
- **Ephem**: 天文计算
- **XGBoost**: 机器学习模型

## 功能特性

### 1. 五运六气分析

```python
# 示例：2023癸卯年五运六气分析
{
    "year": 2023,
    "ganzhi": "癸卯",
    "wuyun": {
        "type": "火运不足",
        "characteristics": ["心系疾病高发", "需注重温补心阳"],
        "diseases_prone": ["心悸", "失眠", "胸痹"]
    },
    "liuqi": {
        "sitian": "厥阴风木",
        "zaiquan": "少阴君火",
        "climate_influence": "风木偏盛，火气不足"
    }
}
```

### 2. 八卦体质分析

```python
# 示例：基于出生信息的八卦体质分析
{
    "birth_info": {
        "date": "1990-03-15",
        "time": "14:30",
        "location": "北京"
    },
    "bagua_analysis": {
        "primary_gua": "离卦",
        "organ_correspondence": "心",
        "constitution_type": "火性体质",
        "characteristics": ["性格急躁", "易上火", "心火旺盛"],
        "health_advice": ["清心降火", "静心养神", "避免过度兴奋"]
    }
}
```

### 3. 子午流注时间医学

```python
# 示例：最佳治疗时间推荐
{
    "condition": "失眠",
    "optimal_treatment_times": [
        {
            "time_period": "亥时 (21:00-23:00)",
            "meridian": "三焦经",
            "treatment": "针刺三焦经穴位",
            "effectiveness": "最佳"
        },
        {
            "time_period": "子时 (23:00-01:00)",
            "meridian": "胆经",
            "treatment": "按摩胆经穴位",
            "effectiveness": "良好"
        }
    ]
}
```

### 4. 个性化体质分析

```python
# 示例：基于八字的体质分析
{
    "bazi": {
        "year": "庚子",
        "month": "戊寅",
        "day": "甲午",
        "hour": "丙寅"
    },
    "wuxing_analysis": {
        "wood": 3,  # 木旺
        "fire": 2,  # 火平
        "earth": 1, # 土弱
        "metal": 1, # 金弱
        "water": 1  # 水弱
    },
    "constitution": {
        "type": "木火偏旺型",
        "characteristics": ["肝火旺盛", "易怒急躁", "筋骨强健"],
        "health_risks": ["高血压", "眼疾", "筋骨损伤"],
        "dietary_advice": ["清肝降火", "滋阴润燥", "少食辛辣"],
        "lifestyle_advice": ["静心养性", "适度运动", "规律作息"]
    }
}
```

## API接口

### 1. 五运六气分析

```http
POST /api/v1/calculation/wuyun-liuqi
Content-Type: application/json

{
    "year": 2024,
    "patient_birth": "1990-03-15",
    "analysis_date": "2024-01-15"
}
```

### 2. 八卦体质分析

```http
POST /api/v1/calculation/bagua-constitution
Content-Type: application/json

{
    "birth_date": "1990-03-15",
    "birth_time": "14:30",
    "birth_location": {
        "latitude": 39.9042,
        "longitude": 116.4074,
        "timezone": "Asia/Shanghai"
    }
}
```

### 3. 子午流注时间推荐

```http
POST /api/v1/calculation/ziwu-liuzhu
Content-Type: application/json

{
    "condition": "失眠",
    "treatment_type": "针灸",
    "date": "2024-01-15"
}
```

### 4. 综合算诊分析

```http
POST /api/v1/calculation/comprehensive-analysis
Content-Type: application/json

{
    "patient_info": {
        "birth_date": "1990-03-15",
        "birth_time": "14:30",
        "birth_location": {
            "latitude": 39.9042,
            "longitude": 116.4074
        }
    },
    "current_symptoms": ["失眠", "心悸", "易怒"],
    "analysis_date": "2024-01-15"
}
```

## 安装和运行

### 环境要求

- Python 3.13.3+
- UV包管理器

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/suokelife/calculation-service.git
cd calculation-service

# 2. 使用UV创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 3. 安装依赖（使用国内镜像）
uv pip install -e .

# 4. 安装开发依赖
uv pip install -e ".[dev]"

# 5. 运行服务
uvicorn calculation_service.cmd.server:app --reload --host 0.0.0.0 --port 8005
```

### Docker运行

```bash
# 构建镜像
docker build -t calculation-service .

# 运行容器
docker run -p 8005:8005 calculation-service
```

## 配置

### 环境变量

```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost/calculation_db
REDIS_URL=redis://localhost:6379

# 服务配置
SERVICE_NAME=calculation-service
SERVICE_PORT=8005
LOG_LEVEL=INFO

# 天文计算配置
ASTRONOMICAL_DATA_PATH=/data/astronomical
TIMEZONE=Asia/Shanghai

# 机器学习模型配置
MODEL_PATH=/models
MODEL_VERSION=v1.0.0
```

## 测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行性能测试
pytest tests/benchmark/

# 生成覆盖率报告
pytest --cov=calculation_service --cov-report=html
```

## 部署

### Kubernetes部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: calculation-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: calculation-service
  template:
    metadata:
      labels:
        app: calculation-service
    spec:
      containers:
      - name: calculation-service
        image: calculation-service:latest
        ports:
        - containerPort: 8005
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

## 监控和日志

### 健康检查

```http
GET /health
```

### 指标监控

```http
GET /metrics
```

### 日志格式

```json
{
    "timestamp": "2024-01-15T10:30:00Z",
    "level": "INFO",
    "service": "calculation-service",
    "module": "wuyun_liuqi",
    "message": "五运六气分析完成",
    "patient_id": "12345",
    "analysis_type": "comprehensive",
    "duration_ms": 150
}
```

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/new-algorithm`)
3. 提交更改 (`git commit -am 'Add new algorithm'`)
4. 推送到分支 (`git push origin feature/new-algorithm`)
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

- 项目主页: https://github.com/suokelife/calculation-service
- 问题反馈: https://github.com/suokelife/calculation-service/issues
- 邮箱: dev@suokelife.com

## 免责声明

本服务提供的算诊分析仅供参考，不能替代专业医疗诊断。请在专业中医师指导下使用相关建议。 