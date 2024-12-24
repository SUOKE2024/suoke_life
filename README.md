# SuoKe Life App

基于 Flutter + GetX 开发的智能生活助手应用，集成多个专业AI助手。

## 功能特性

### AI助手团队

1. 小艾 - 生活助理
- 生活建议和解决方案
- 多维数据采集和分析
- 实时行为分析和场景识别
- LIFE频道数据管理

2. 老克 - 知识助理
- 技术架构咨询
- 专业知识库管理
- 知识图谱分析
- GraphRAG技术支持

3. 小克 - 商务助理
- 市场趋势分析
- 供应链管理
- 商业决策支持
- 农产品预制服务

### 核心功能
- 健康管理
- 生活记录
- 知识探索
- 系统管理

## 技术栈

- Flutter 3.16.0
- Dart 3.2.0
- GetX 4.6.6
- 豆包 API v3

## 项目结构

```
lib/
├── app/
│   ├── core/          # 核心功能
│   │   ├── config/    # 配置文件
│   │   ├── network/   # 网络服务
│   │   ├── storage/   # 存储服务
│   │   └── theme/     # 主题配置
│   ├── data/          # 数据层
│   ├── modules/       # 业务模块
│   ├── presentation/  # 表现层
│   ├── routes/        # 路由
│   └── services/      # 服务层
```

## 开发环境配置

1. 环境要求
- Flutter SDK
- Android Studio / VS Code
- 豆包 API Key

2. 启动步骤
```bash
# 安装依赖
flutter pub get

# 运行项目
flutter run
```

## 文档

详细文档请参考:
- [API文档](docs/api/README.md)
- [部署指南](docs/deployment/README.md)
- [安全规范](docs/security/README.md)
- [UI设计规范](docs/ui/README.md)
