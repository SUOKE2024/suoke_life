# Utility Services

这是一个合并后的微服务，包含以下原始服务：

- integration-service
- medical-resource-service
- corn-maze-service

## 架构说明

本服务通过合并多个相关微服务来简化架构，提高维护效率。

## 启动方式

```bash
docker build -t utility-services .
docker run -p 8000:8000 utility-services
```

## API文档

各子服务的API文档位于 `api/` 目录下。

## 子服务说明

### integration-service
- 代码位置: `utility_services/integration_service/`
- API文档: `api/integration-service/`
- 配置文件: `config/integration-service/`

### medical-resource-service
- 代码位置: `utility_services/medical_resource_service/`
- API文档: `api/medical-resource-service/`
- 配置文件: `config/medical-resource-service/`

### corn-maze-service
- 代码位置: `utility_services/corn_maze_service/`
- API文档: `api/corn-maze-service/`
- 配置文件: `config/corn-maze-service/`

