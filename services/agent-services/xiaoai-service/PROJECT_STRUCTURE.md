# 小艾智能体服务项目结构

## 概述

本项目采用标准的 Python 包结构，符合 Python 项目的最佳实践。

## 目录结构

```
xiaoai-service/
├── xiaoai/                          # 主包目录
│   ├── __init__.py                  # 包初始化文件
│   ├── agent/                       # 智能体相关模块
│   │   ├── __init__.py
│   │   ├── agent_manager.py         # 智能体管理器
│   │   ├── model_factory.py         # 模型工厂
│   │   └── ...
│   ├── api/                         # API 相关（如果有内部 API）
│   ├── cli/                         # 命令行工具
│   │   ├── __init__.py
│   │   ├── main.py                  # 主启动脚本
│   │   └── server.py                # 服务器脚本
│   ├── config/                      # 配置管理
│   ├── delivery/                    # 交付层（gRPC/HTTP 服务实现）
│   │   ├── __init__.py
│   │   ├── xiaoai_service_impl.py   # 主服务实现
│   │   └── api/                     # API 处理器
│   ├── domain/                      # 领域模型
│   ├── four_diagnosis/              # 四诊功能模块
│   │   ├── __init__.py
│   │   ├── coordinator/             # 协调器
│   │   ├── fusion/                  # 融合引擎
│   │   ├── reasoning/               # 推理引擎
│   │   ├── recommendation/          # 推荐系统
│   │   └── validation/              # 验证器
│   ├── gateway/                     # 网关
│   ├── integration/                 # 外部集成
│   ├── observability/              # 可观测性（监控、日志等）
│   ├── orchestrator/               # 编排器
│   ├── repository/                 # 数据仓储
│   ├── resilience/                 # 弹性组件（熔断器等）
│   ├── service/                    # 业务服务
│   └── utils/                      # 工具类
├── api/                            # gRPC/API 定义
│   ├── __init__.py
│   └── grpc/                       # gRPC 协议文件
├── tests/                          # 测试目录
│   ├── __init__.py
│   ├── unit/                       # 单元测试
│   ├── integration/                # 集成测试
│   ├── e2e/                        # 端到端测试
│   └── performance/                # 性能测试
├── config/                         # 配置文件
├── docs/                           # 文档
├── examples/                       # 示例代码
├── scripts/                        # 脚本
├── templates/                      # 模板文件
├── deploy/                         # 部署相关
├── dev_tools/                      # 开发工具
├── integration/                    # 外部服务集成客户端
├── logs/                           # 日志目录
├── data/                           # 数据目录
├── setup.py                        # 包安装配置
├── requirements.txt                # 依赖列表
├── requirements_optimized.txt      # 优化的依赖列表
├── MANIFEST.in                     # 包清单
├── Dockerfile                      # Docker 配置
├── docker-compose.yml             # Docker Compose 配置
├── run_server.py                   # 服务启动脚本
└── README.md                       # 项目说明
```

## 主要变更

从之前的 Go 风格目录结构（`cmd/`, `internal/`, `pkg/`）调整为标准的 Python 包结构：

1. **主包目录**: 创建了 `xiaoai/` 作为主包目录
2. **命令行工具**: 将 `cmd/` 重构为 `xiaoai/cli/`
3. **内部模块**: 将 `internal/` 下的模块移动到 `xiaoai/` 下
4. **工具包**: 将 `pkg/utils/` 移动到 `xiaoai/utils/`
5. **导入路径**: 更新所有导入路径以适应新结构

## 启动方式

### 方式一：使用启动脚本
```bash
python run_server.py
```

### 方式二：使用模块方式
```bash
python -m xiaoai.cli.main
```

### 方式三：安装后使用命令行
```bash
pip install -e .
xiaoai-server
```

## 开发指南

1. **添加新模块**: 在 `xiaoai/` 下创建新的子包
2. **导入规则**: 使用相对导入（`from ..module import something`）
3. **测试**: 在 `tests/` 下创建对应的测试文件
4. **配置**: 配置文件放在 `config/` 目录下

## 符合的 Python 最佳实践

1. ✅ 标准的包结构
2. ✅ 正确的 `__init__.py` 文件
3. ✅ 合理的模块组织
4. ✅ 标准的 `setup.py` 配置
5. ✅ 清晰的依赖管理
6. ✅ 完整的测试结构
7. ✅ 文档和示例
8. ✅ 容器化支持 