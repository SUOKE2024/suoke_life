# 索克生活项目脚本

本目录包含了索克生活项目的各种自动化脚本和工具。

## 📁 目录结构

### 🔧 设置脚本 (`setup/`)
用于环境设置和项目初始化的脚本：
- 开发环境配置
- 依赖安装
- 服务启动脚本

### 🏗️ 构建脚本 (`build/`)
用于项目构建和打包的脚本：
- 前端构建
- 后端打包
- Docker镜像构建

### 🚀 部署脚本 (`deploy/`)
用于项目部署的脚本：
- 生产环境部署
- 测试环境部署
- 容器编排

### 🧪 测试脚本 (`test/`)
用于自动化测试的脚本：
- 单元测试
- 集成测试
- 端到端测试
- 性能测试

### 🔧 维护脚本 (`maintenance/`)
用于项目维护的脚本：
- 数据库迁移
- 版本更新
- 清理任务
- 修复脚本

### 🛠️ 工具脚本 (`tools/`)
各种实用工具脚本：
- 代码分析
- 数据处理
- 监控工具
- 验证脚本

## 🚀 常用脚本

### 快速启动
```bash
# 启动开发环境
./setup/start_local_services.sh

# 快速测试
./test/quick-test.js
```

### 部署相关
```bash
# 部署到测试环境
./deploy/deploy_phase1.sh

# 生产环境部署
./deploy/production_deploy.sh
```

### 维护任务
```bash
# Python版本更新
python maintenance/update_python_version.py

# 项目清理
./maintenance/project-cleanup.sh
```

## 📋 使用规范

1. **权限设置**: 确保脚本有执行权限
   ```bash
   chmod +x script_name.sh
   ```

2. **环境变量**: 某些脚本需要设置环境变量，请查看脚本头部注释

3. **依赖检查**: 运行前确保所需依赖已安装

4. **日志记录**: 重要操作会生成日志文件

## 🔍 脚本开发指南

### Shell脚本规范
- 使用 `#!/bin/bash` 作为shebang
- 添加错误处理 `set -e`
- 包含使用说明和示例

### Python脚本规范
- 使用Python 3.13.3
- 包含类型注解
- 添加docstring文档
- 遵循PEP 8代码风格

### JavaScript脚本规范
- 使用ES6+语法
- 添加JSDoc注释
- 错误处理和日志记录

## 🆘 故障排除

如果脚本执行遇到问题：

1. 检查权限设置
2. 验证环境变量
3. 查看错误日志
4. 参考脚本内的注释说明

## 🔗 相关文档

- [开发指南](../docs/guides/DEVELOPMENT.md)
- [部署指南](../docs/guides/DEPLOYMENT.md)
- [项目文档](../docs/README.md)

---

**最后更新**: 2025-05-27 15:51:51  
**维护者**: Song Xu <song.xu@icloud.com> 