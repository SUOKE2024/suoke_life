# SUOKE-LIFE (索克生活)

<p align="center">
  <img src="assets/images/logo.png" alt="SUOKE-LIFE Logo" width="200"/>
  <br>
  <em>智能化生活助手平台</em>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Flutter-3.16+-blue.svg" alt="Flutter"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/FastAPI-0.100+-blue.svg" alt="FastAPI"></a>
</p>

## 📱 项目概览

索克生活是一个基于 AI 的智能化生活助手平台，致力于为用户提供个性化的生活方式指导和优化建议。通过多维数据分析、AI 赋能和本地化隐私保护，为用户打造智能、安全、温暖的数字生活空间。

### 🌟 核心特性

- 🤖 **智能助手系统**
  - 生活助理（小艾）：日常生活建议和情感支持
  - 知识助理（老克）：知识学习和个人成长顾问
  - 商务助理（小克）：工作效率和决策支持

- 🎯 **生活方式引擎**
  - 社交运动：智能匹配运动伙伴
  - 生活优化：个性化建议和习惯养成
  - 会员价值：会员俱乐部连接

- 📊 **数据中心**
  - 健康数据可视化
  - 生活记录追踪
  - 个人成长分析

## 🛠 技术栈

### 前端
- Flutter 3.16+
- Material Design 3
- GetX 状态管理
- 本地化存储

### 后端
- FastAPI + Flask
- PostgreSQL 15+
- Redis 7.0+
- OSS 对象存储

### AI 模型
- doubao-pro-32k (ep-20241207123426-72mnv)
- doubao-pro-128k (ep-20241207124106-4b5xn)
- doubao-embedding (ep-20241207124339-rh46z)

## 🚀 快速开始

### 环境要求
- Flutter 3.16+
- Python 3.11+
- PostgreSQL 15+
- Redis 7.0+
- Node.js 18+
- Git

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/SUOKE2024/suoke_life.git
cd suoke_life
```

2. **安装依赖**
```bash
# Flutter 依赖
flutter pub get

# Python 依赖
pip install -r requirements.txt

# 环境配置
cp .env.example .env
```

3. **配置数据库**
```bash
# 创建数据库
python scripts/create_db.py

# 运行迁移
python scripts/migrate.py
```

4. **启动服务**
```bash
# 启动后端服务
python server/main.py

# 运行 Flutter 应用
flutter run
```

## 📖 项目文档

- [架构设计](docs/project/architecture.md)
- [API 文档](docs/project/api_design.md)
- [数据库设计](docs/project/database_design.md)
- [安全架构](docs/project/security.md)
- [用户指南](docs/project/user_guide.md)
- [开发指南](docs/project/development_guide.md)
- [测试文档](docs/project/testing.md)

## 🤝 贡献指南

1. Fork 项目并创建功能分支
2. 遵循项目的代码规范和提交规范
3. 编写测试并确保通过
4. 提交 Pull Request

### 提交规范

```
feat: 新功能
fix: 修复问题
docs: 文档更新
style: 代码格式
refactor: 代码重构
test: 测试相关
chore: 构建过程或辅助工具的变动
```

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)

## 📞 联系我们

- 官网：[https://suoke.life](https://suoke.life)
- 邮箱：support@suoke.life
- 微信：SUOKE-LIFE

## 🙏 鸣谢

感谢所有为项目做出贡献的开发者！