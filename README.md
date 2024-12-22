# 索克生活 (SuoKe Life)

一个基于 Flutter 的现代化生活服务应用。

## 项目结构

```
lib/
  ├── app/
  │   ├── core/           # 核心功能（配置、依赖注入等）
  │   ├── data/          # 数据层（模型、数据库等）
  │   ├── services/      # 服务层（API、本地存储等）
  │   └── presentation/  # 表现层（页面、控制器等）
  └── main.dart          # 入口文件
```

## 功能特性

- 智能助手
  - 小艾：生活管家
  - 老克：知识顾问
  - 小克：商务助手
- 聊天系统
  - 文本消息
  - 语音消息
  - 图片消息
- 数据存储
  - SQLite 本地数据库
  - 环境变量配置

## 开发环境

- Flutter: 3.x
- Dart: 3.x
- GetX: 最新版
- SQLite: 最新版

## 安装与运行

1. 克隆项目:
```bash
git clone https://github.com/SUOKE2024/suoke_life.git
```

2. 安装依赖:
```bash
flutter pub get
```

3. 配置环境变量:
```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的配置
```

4. 运行项目:
```bash
flutter run
```

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系我们

- 项目负责人: [Your Name]
- 邮箱: [Your Email]
