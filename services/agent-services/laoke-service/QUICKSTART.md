# 老克智能体服务快速启动指南

## 🚀 快速启动

### 方式一：使用简化启动脚本（推荐）

```bash
# 直接运行简化启动脚本
./start_simple.sh
```

该脚本会自动：
- 检查Python环境
- 创建虚拟环境
- 安装基本依赖
- 启动服务

### 方式二：手动启动

```bash
# 1. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装依赖
pip install --upgrade pip
pip install fastapi uvicorn pydantic loguru pyyaml openai aiohttp

# 3. 设置环境变量
export PYTHONPATH="$(pwd):$PYTHONPATH"
export SERVICE__ENVIRONMENT="development"
export SERVICE__DEBUG="true"

# 4. 启动服务
python main.py
```

## 📝 配置说明

### 环境变量

可以通过环境变量进行配置：

```bash
# 服务配置
export SERVICE__ENVIRONMENT="development"  # 环境：development/production
export SERVICE__DEBUG="true"              # 调试模式
export SERVICE__VERSION="1.0.0"           # 服务版本

# 服务器配置
export SERVER__REST_HOST="0.0.0.0"        # REST服务器地址
export SERVER__REST_PORT="8080"           # REST服务器端口
export SERVER__GRPC_HOST="0.0.0.0"        # gRPC服务器地址
export SERVER__GRPC_PORT="8081"           # gRPC服务器端口

# AI模型配置
export MODELS__API_KEY="your-openai-api-key"     # OpenAI API密钥
export MODELS__BASE_URL="https://api.openai.com/v1"  # API基础URL
export MODELS__PRIMARY_MODEL="gpt-4o-mini"       # 主要模型
export MODELS__TEMPERATURE="0.7"                 # 温度参数

# 无障碍服务配置
export EXTERNAL_SERVICES__ACCESSIBILITY_SERVICE_ENABLED="true"
export EXTERNAL_SERVICES__ACCESSIBILITY_SERVICE_URL="http://localhost:9000"
export EXTERNAL_SERVICES__ACCESSIBILITY_SERVICE_API_KEY="your-accessibility-api-key"
```

### 配置文件

也可以使用YAML配置文件：

```yaml
# config/config.yaml
service:
  name: "老克智能体服务"
  version: "1.0.0"
  environment: "development"
  debug: true

server:
  rest_host: "0.0.0.0"
  rest_port: 8080
  grpc_host: "0.0.0.0"
  grpc_port: 8081

agent:
  models:
    primary_model: "gpt-4o-mini"
    api_key: "your-openai-api-key"
    base_url: "https://api.openai.com/v1"
    temperature: 0.7
    max_tokens: 4096
  
  conversation:
    system_prompt: "你是老克，一个专注于中医知识传播的智能体。"
    max_history_turns: 10
    max_tokens_per_message: 4096

external_services:
  accessibility_service_enabled: true
  accessibility_service_url: "http://localhost:9000"
  accessibility_service_api_key: "your-accessibility-api-key"
  accessibility_service_timeout: 30
```

## 📊 API接口

服务启动后，可以访问以下接口：

### 基本接口

- `GET /` - 服务信息
- `GET /health` - 健康检查
- `GET /stats` - 统计信息

### 会话管理

- `POST /sessions` - 创建会话
- `GET /sessions/{session_id}` - 获取会话信息
- `DELETE /sessions/{session_id}` - 终止会话

### 对话交互

- `POST /sessions/{session_id}/chat` - 发送消息
- `GET /sessions/{session_id}/history` - 获取对话历史

### 无障碍功能

- `POST /accessibility/tts` - 文本转语音
- `POST /accessibility/stt` - 语音转文本
- `GET /accessibility/users/{user_id}/profile` - 获取用户无障碍配置

## 📝 使用示例

### 1. 创建会话

```bash
curl -X POST "http://localhost:8080/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "metadata": {
      "source": "web",
      "device": "desktop"
    }
  }'
```

### 2. 发送消息

```bash
curl -X POST "http://localhost:8080/sessions/{session_id}/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，请介绍一下中医的基本理念",
    "stream": false
  }'
```

### 3. 文本转语音

```bash
curl -X POST "http://localhost:8080/accessibility/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，欢迎使用老克智能体",
    "voice": "female_standard",
    "speed": "normal",
    "language": "zh-CN"
  }'
```

## 🔧 开发调试

### 查看日志

日志文件位于 `logs/` 目录下：

```bash
# 查看实时日志
tail -f logs/laoke-service.log

# 查看错误日志
tail -f logs/error.log
```

### 运行测试

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov

# 运行单元测试
pytest tests/test_agent.py -v

# 运行集成测试
pytest tests/test_integration.py -v

# 运行所有测试
pytest tests/ -v --cov=laoke_service
```

### 性能监控

服务提供了内置的性能监控接口：

```bash
# 查看服务统计
curl http://localhost:8080/stats

# 查看健康状态
curl http://localhost:8080/health
```

## ⚠️ 注意事项

1. **API密钥配置**：请确保配置了正确的OpenAI API密钥
2. **网络访问**：确保能够访问 OpenAI API服务
3. **端口冲突**：默认端口8080，如有冲突请修改配置
4. **内存使用**：服务会缓存会话数据，注意内存使用情况

## 🔗 相关链接

- [项目主页](../../../README.md)
- [API文档](docs/API.md)
- [部署指南](docs/DEPLOYMENT.md)
- [开发指南](docs/DEVELOPMENT.md)
