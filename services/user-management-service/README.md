# User Management Service

这是一个合并后的微服务，包含以下原始服务：

- auth-service
- user-service

## 架构说明

本服务通过合并多个相关微服务来简化架构，提高维护效率。

## 启动方式

```bash
docker build -t user-management-service .
docker run -p 8000:8000 user-management-service
```

## API文档

各子服务的API文档位于 `api/` 目录下。
