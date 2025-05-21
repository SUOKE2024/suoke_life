# Corn Maze Service 开发指南

本文档提供 Corn Maze Service 的开发指南，包括环境配置、代码结构、开发流程和最佳实践。

## 目录

- [开发环境配置](#开发环境配置)
- [项目结构](#项目结构)
- [开发流程](#开发流程)
- [测试指南](#测试指南)
- [代码风格](#代码风格)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

## 开发环境配置

### 依赖项

- Python 3.8+
- gRPC
- NetworkX (用于迷宫生成算法)
- Redis (可选，用于缓存)
- MongoDB (用于数据存储)

### 环境设置

1. 克隆仓库并进入项目目录:

```bash
git clone https://github.com/suoke-life/corn-maze-service.git
cd corn-maze-service
```

2. 创建并激活虚拟环境:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

3. 安装依赖:

```bash
pip install -r requirements.txt
```

4. 生成 gRPC 代码:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. api/grpc/corn_maze.proto
```

## 项目结构

```
corn-maze-service/
├── api/                    # API 定义
│   └── grpc/               # gRPC 接口定义
├── cmd/                    # 命令行入口
│   └── server/             # 服务主入口
├── config/                 # 配置文件
├── data/                   # 数据目录
├── deploy/                 # 部署配置
│   ├── docker/             # Docker 配置
│   └── kubernetes/         # Kubernetes 配置
├── docs/                   # 文档
├── internal/               # 内部代码
│   ├── delivery/           # 服务交付层
│   │   └── grpc/           # gRPC 实现
│   ├── maze/               # 迷宫生成和管理
│   ├── model/              # 数据模型
│   ├── repository/         # 数据访问层
│   └── service/            # 业务逻辑层
├── pkg/                    # 公共包
│   └── utils/              # 工具函数
└── test/                   # 测试代码
    ├── client/             # 客户端测试工具
    └── integration/        # 集成测试
```

## 开发流程

### 新功能开发流程

1. 创建功能分支
```bash
git checkout -b feature/your-feature-name
```

2. 实现功能并添加测试
3. 确保所有测试通过
```bash
python -m unittest discover
```

4. 提交代码并创建合并请求
```bash
git add .
git commit -m "feat: 添加新功能描述"
git push origin feature/your-feature-name
```

### 迷宫生成逻辑开发

迷宫生成是本服务的核心功能，主要在 `internal/maze/generator.py` 中实现。开发新的迷宫生成算法或修改现有算法时，请确保遵循以下准则:

1. 使用 `NetworkX` 库处理迷宫的图结构
2. 确保迷宫有明确的起点和终点
3. 根据用户的健康属性动态调整迷宫内容
4. 添加足够的单元测试验证算法正确性
5. 考虑算法的性能，避免过度计算

### 数据模型扩展

扩展数据模型时，请遵循以下步骤:

1. 在 `internal/model` 中添加新的模型类
2. 实现 `to_dict` 和 `from_dict` 方法
3. 在 `internal/repository` 中添加对应的存储方法
4. 添加单元测试

## 测试指南

### 运行单元测试

```bash
python -m unittest discover test
```

### 运行特定测试

```bash
python -m unittest test.test_maze_generator
```

### 运行集成测试

```bash
python -m unittest discover test.integration
```

### 测试覆盖率

```bash
coverage run -m unittest discover
coverage report
coverage html  # 生成HTML报告
```

## 代码风格

本项目遵循 PEP 8 规范，并使用以下工具确保代码质量:

- `black`: 代码格式化
- `isort`: 导入排序
- `flake8`: 代码静态检查
- `mypy`: 类型检查

运行代码质量检查:

```bash
black .
isort .
flake8
mypy .
```

## 最佳实践

### 日志记录

使用标准库的 logging 模块，并遵循服务的日志级别约定:

- DEBUG: 详细的开发信息
- INFO: 常规操作信息
- WARNING: 可能的问题或轻微错误
- ERROR: 严重问题但服务仍可运行
- CRITICAL: 导致服务无法继续的严重错误

示例:
```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.info("操作开始")
    try:
        # 业务逻辑
        logger.debug("处理中的详细信息")
    except Exception as e:
        logger.error(f"发生错误: {e}", exc_info=True)
```

### 错误处理

- 使用明确的错误类型
- 在日志中记录异常信息
- 向客户端返回友好的错误消息

### 异步处理

使用异步函数处理I/O密集型操作:

```python
async def get_knowledge_nodes():
    # 异步获取知识节点
    pass
```

## 故障排除

### 常见问题

1. **服务无法启动**

   检查:
   - 配置文件是否正确
   - 所需端口是否被占用
   - 依赖服务(如MongoDB)是否可访问

2. **gRPC生成代码问题**

   重新生成gRPC代码:
   ```bash
   python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. api/grpc/corn_maze.proto
   ```

3. **迷宫生成性能问题**

   - 检查算法复杂度
   - 考虑使用缓存
   - 对大型迷宫使用异步生成

### 获取帮助

如有其他问题，请联系开发团队或提交GitHub issue。 