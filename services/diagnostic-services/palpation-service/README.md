# 索克生活 - 触诊服务 (Palpation Service)

## 项目简介

触诊服务是索克生活健康管理平台的核心组件之一，专注于中医触诊的数字化和智能化。该服务集成了脉诊、腹诊、皮肤触诊等多种触诊技术，通过现代传感器技术和人工智能算法，实现传统中医触诊的科学化分析和个性化健康评估。

### 核心功能

- **🫀 脉诊分析**: 支持多种脉诊设备，实时采集和分析脉象数据
- **🤲 腹诊检测**: 腹部触诊压力分析和体征识别
- **🖐️ 皮肤触诊**: 皮肤温度、湿度、弹性等多维度检测
- **🧠 AI智能分析**: 基于深度学习的中医证型识别和健康评估
- **📊 数据可视化**: 丰富的图表展示和趋势分析
- **📋 智能报告**: 个性化健康报告生成和建议推荐
- **⚡ 实时监控**: 设备状态监控和系统性能监控
- **🔄 预测分析**: 基于历史数据的健康趋势预测

### 技术特点

- **高性能**: 异步处理、并行计算、多层缓存优化
- **实时性**: 支持流式数据处理和实时特征提取
- **智能化**: 集成多种AI模型和机器学习算法
- **可扩展**: 模块化设计，支持多设备接入和功能扩展
- **可靠性**: 完善的错误处理、自动恢复和健康监控

## 系统架构

```
触诊服务架构
├── API层 (FastAPI)
│   ├── REST API接口
│   ├── WebSocket实时通信
│   └── gRPC服务接口
├── 业务逻辑层
│   ├── 设备管理器 (Device Manager)
│   ├── 数据处理器 (Data Processor)
│   ├── AI分析器 (AI Analyzer)
│   ├── 报告生成器 (Report Generator)
│   └── 预测分析器 (Predictive Analyzer)
├── 数据层
│   ├── SQLite数据库
│   ├── Redis缓存
│   └── 文件存储
└── 基础设施层
    ├── 配置管理
    ├── 日志系统
    ├── 监控告警
    └── 安全认证
```

## 快速开始

### 系统要求

- **操作系统**: Linux (Ubuntu 18.04+) / macOS (10.15+)
- **Python**: 3.8 或更高版本
- **内存**: 至少 4GB RAM
- **存储**: 至少 10GB 可用空间
- **网络**: 支持HTTP/HTTPS和WebSocket

### 自动安装 (推荐)

```bash
# 克隆项目
git clone <repository-url>
cd palpation-service

# 运行自动安装脚本
chmod +x scripts/setup.sh
./scripts/setup.sh
```

安装脚本将自动完成以下步骤：
1. 检查系统要求
2. 安装系统依赖
3. 创建Python虚拟环境
4. 安装Python依赖包
5. 初始化数据库
6. 配置服务
7. 运行基础测试

### 手动安装

#### 1. 安装系统依赖

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y build-essential python3-dev python3-pip python3-venv \
    libffi-dev libssl-dev libjpeg-dev libpng-dev libfreetype6-dev \
    libblas-dev liblapack-dev libatlas-base-dev gfortran libhdf5-dev \
    libopencv-dev portaudio19-dev libasound2-dev libusb-1.0-0-dev \
    libudev-dev bluetooth libbluetooth-dev i2c-tools
```

**macOS:**
```bash
# 安装Homebrew (如果未安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装依赖
brew install python@3.11 libffi openssl jpeg libpng freetype \
    openblas lapack hdf5 opencv portaudio libusb
```

#### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
```

#### 3. 安装Python依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. 配置服务

```bash
# 复制配置文件模板
cp config/palpation.yaml.example config/palpation.yaml

# 编辑配置文件
nano config/palpation.yaml
```

#### 5. 初始化数据库

```bash
python -c "
import sqlite3
import os

os.makedirs('data', exist_ok=True)
conn = sqlite3.connect('data/palpation.db')
# 数据库初始化代码...
conn.close()
"
```

## 配置说明

### 主配置文件 (config/palpation.yaml)

```yaml
# 服务配置
service:
  name: "palpation-service"
  host: "0.0.0.0"
  port: 8000
  debug: false
  workers: 4

# 数据库配置
database:
  type: "sqlite"
  path: "data/palpation.db"
  pool_size: 10

# 缓存配置
cache:
  enabled: true
  redis_host: "localhost"
  redis_port: 6379
  ttl: 3600

# AI模型配置
ai_models:
  pulse_analysis:
    model_path: "models/pulse_classifier.pkl"
    confidence_threshold: 0.8
  
  tcm_syndrome:
    model_path: "models/tcm_syndrome.pkl"
    feature_extractor: "traditional"
```

### 设备配置 (config/devices.yaml)

```yaml
# 脉诊设备配置
pulse_devices:
  primary_pulse_sensor:
    enabled: true
    device_type: "pulse_sensor"
    connection:
      type: "serial"
      port: "/dev/ttyUSB0"
      baudrate: 9600
    sampling:
      rate: 1000  # Hz
      duration: 60  # 秒
      channels: 3  # 寸关尺三部
```

### 环境变量 (.env)

```bash
# 服务配置
PALPATION_SERVICE_HOST=0.0.0.0
PALPATION_SERVICE_PORT=8000
PALPATION_SERVICE_DEBUG=false

# 数据库配置
PALPATION_DATABASE_PATH=data/palpation.db

# 缓存配置
PALPATION_CACHE_REDIS_HOST=localhost
PALPATION_CACHE_REDIS_PORT=6379

# 日志配置
PALPATION_LOGGING_LEVEL=INFO
```

## 使用指南

### 启动服务

#### 本地启动
```bash
# 激活虚拟环境
source venv/bin/activate

# 启动服务
python main.py

# 或使用启动脚本
./start_service.sh
```

#### Docker启动
```bash
# 构建镜像
docker build -t palpation-service:latest .

# 启动单个容器
docker run -d -p 8000:8000 --name palpation-service palpation-service:latest

# 或使用Docker Compose启动完整环境
docker-compose up -d
```

### API接口

#### 健康检查
```bash
curl http://localhost:8000/health
```

#### 创建触诊会话
```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "device_type": "pulse_sensor",
    "session_config": {
      "duration": 60,
      "sampling_rate": 1000
    }
  }'
```

#### 获取分析结果
```bash
curl http://localhost:8000/api/v1/sessions/{session_id}/analysis
```

#### 生成健康报告
```bash
curl -X POST http://localhost:8000/api/v1/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session123",
    "report_type": "detailed",
    "language": "zh-CN"
  }'
```

### WebSocket实时通信

```javascript
// 连接WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/realtime');

// 监听实时数据
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('实时数据:', data);
};

// 发送控制命令
ws.send(JSON.stringify({
    type: 'start_session',
    session_id: 'session123'
}));
```

## 监控和运维

### 访问监控仪表板

- **服务监控**: http://localhost:8080
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Kibana**: http://localhost:5601

### 查看日志

```bash
# 查看服务日志
tail -f logs/palpation.log

# 查看错误日志
tail -f logs/error.log

# 使用Docker查看日志
docker logs -f palpation-service
```

### 数据备份

```bash
# 手动备份
./scripts/backup.sh

# 查看备份文件
ls -la backups/

# 恢复备份
./scripts/restore.sh backups/palpation_backup_20231201_120000.tar.gz
```

### 性能监控

```bash
# 查看系统资源使用
curl http://localhost:8000/api/v1/system/stats

# 查看缓存统计
curl http://localhost:8000/api/v1/cache/stats

# 查看设备状态
curl http://localhost:8000/api/v1/devices/status
```

## 开发指南

### 项目结构

```
palpation-service/
├── main.py                 # 主启动文件
├── requirements.txt        # Python依赖
├── Dockerfile             # Docker配置
├── docker-compose.yml     # Docker Compose配置
├── config/                # 配置文件
│   ├── palpation.yaml
│   └── devices.yaml
├── internal/              # 内部模块
│   ├── analysis/          # 分析模块
│   ├── cache/             # 缓存管理
│   ├── config/            # 配置管理
│   ├── coordination/      # 服务协调
│   ├── devices/           # 设备管理
│   ├── fusion/            # 数据融合
│   ├── monitoring/        # 监控模块
│   ├── prediction/        # 预测分析
│   ├── processing/        # 数据处理
│   ├── reports/           # 报告生成
│   └── visualization/     # 数据可视化
├── api/                   # API接口
├── data/                  # 数据存储
├── logs/                  # 日志文件
├── models/                # AI模型
├── reports/               # 生成的报告
├── scripts/               # 脚本文件
└── test/                  # 测试文件
```

### 添加新设备

1. 在 `config/devices.yaml` 中添加设备配置
2. 在 `internal/devices/` 中实现设备驱动
3. 在设备管理器中注册新设备
4. 添加相应的测试用例

### 扩展AI模型

1. 在 `internal/analysis/` 中添加新的分析器
2. 训练和保存模型到 `models/` 目录
3. 更新配置文件中的模型路径
4. 在AI分析器中集成新模型

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest test/test_devices.py

# 运行测试并生成覆盖率报告
pytest --cov=internal --cov-report=html
```

### 代码质量检查

```bash
# 代码格式化
black internal/ test/

# 代码风格检查
flake8 internal/ test/

# 类型检查
mypy internal/

# 安全检查
bandit -r internal/
```

## 故障排除

### 常见问题

#### 1. 服务启动失败

**问题**: `ModuleNotFoundError: No module named 'xxx'`
**解决**: 确保虚拟环境已激活并安装了所有依赖
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. 设备连接失败

**问题**: 无法连接到串口设备
**解决**: 检查设备权限和连接
```bash
# 检查设备是否存在
ls -la /dev/ttyUSB*

# 添加用户到dialout组
sudo usermod -a -G dialout $USER

# 重新登录或重启
```

#### 3. 数据库连接错误

**问题**: `sqlite3.OperationalError: database is locked`
**解决**: 检查数据库文件权限和进程
```bash
# 检查数据库文件
ls -la data/palpation.db

# 检查是否有其他进程占用
lsof data/palpation.db
```

#### 4. 内存不足

**问题**: 服务运行时内存使用过高
**解决**: 调整配置参数
```yaml
# 在config/palpation.yaml中调整
cache:
  max_memory: 52428800  # 50MB
  
ai_models:
  batch_size: 32  # 减小批处理大小
```

### 日志分析

```bash
# 查看错误日志
grep "ERROR" logs/palpation.log

# 查看特定时间段的日志
grep "2023-12-01 10:" logs/palpation.log

# 统计错误类型
grep "ERROR" logs/palpation.log | awk '{print $4}' | sort | uniq -c
```

### 性能优化

1. **缓存优化**: 调整缓存策略和大小
2. **数据库优化**: 添加索引，优化查询
3. **并发优化**: 调整工作进程数量
4. **内存优化**: 使用内存分析工具找出内存泄漏

## API文档

完整的API文档可以通过以下方式访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 代码规范

- 遵循 PEP 8 Python 代码风格
- 使用类型注解
- 编写单元测试
- 添加适当的文档字符串
- 保持代码简洁和可读性

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- **项目维护者**: 索克生活开发团队
- **邮箱**: dev@suokelife.com
- **文档**: https://docs.suokelife.com/palpation-service
- **问题反馈**: https://github.com/suokelife/palpation-service/issues

## 更新日志

### v1.0.0 (2023-12-01)
- 初始版本发布
- 支持脉诊、腹诊、皮肤触诊
- 集成AI分析和报告生成
- 完整的监控和运维功能

---

**索克生活 - 让健康管理更智能** 🌟 