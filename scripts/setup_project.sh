#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}开始创建项目结构...${NC}"

# 创建目录结构
mkdir -p lib/app/{core,features,presentation}/{config,constants,di,models,repositories,services,utils}
mkdir -p lib/app/core/{analytics,api,auth,cache,database,error,localization,network,router,security,storage,theme}
mkdir -p lib/app/features/{ai,chat,explore,health,life,profile,suoke}
mkdir -p lib/app/presentation/{pages,widgets,theme}
mkdir -p test/{unit,widget,integration}
mkdir -p assets/{images,icons,config,fonts}
mkdir -p docs/{api,architecture,guides}

# 创建基础文件
touch lib/app/core/config/app_config.dart
touch lib/app/core/constants/app_constants.dart
touch lib/app/core/di/injection.dart
touch lib/app/core/router/app_router.dart
touch lib/app/core/theme/app_theme.dart

# 创建 .env.example
cat > .env.example << EOL
# API Keys
AI_SERVICE_KEY=your_ai_service_key
FIREBASE_API_KEY=your_firebase_key

# Services
API_BASE_URL=https://api.example.com
WEBSOCKET_URL=wss://ws.example.com

# Features
ENABLE_ANALYTICS=true
ENABLE_CRASH_REPORTING=true

# Environment
ENV=development
DEBUG=true
EOL

# 创建 README.md
cat > README.md << EOL
# 搜客生活 App

## 项目简介
搜客生活是一个集成AI助手、健康管理、生活服务于一体的综合性应用。

## 开发环境
- Flutter: 3.16.0
- Dart: 3.2.3
- iOS: 13.0+
- Android: 5.0+

## 项目结构
\`\`\`
lib/
├── app/
│   ├── core/           # 核心功能
│   ├── features/       # 业务功能
│   └── presentation/   # UI 层
├── config/            # 配置
└── main.dart
\`\`\`

## 开始使用
1. 克隆项目
2. 运行 \`flutter pub get\`
3. 复制 \`.env.example\` 到 \`.env\` 并配置环境变量
4. 运行 \`flutter run\`

## 测试
- 单元测试: \`flutter test\`
- 集成测试: \`./scripts/run_device_tests.sh\`

## 文档
详细文档请查看 \`/docs\` 目录
EOL

# 创建 analysis_options.yaml
cat > analysis_options.yaml << EOL
include: package:flutter_lints/flutter.yaml

linter:
  rules:
    - always_declare_return_types
    - avoid_print
    - avoid_empty_else
    - prefer_const_constructors
    - prefer_final_fields
    - prefer_final_locals
    - sort_child_properties_last
    - use_key_in_widget_constructors

analyzer:
  errors:
    missing_required_param: error
    missing_return: error
    must_be_immutable: error
  exclude:
    - "**/*.g.dart"
    - "**/*.freezed.dart"
EOL

echo -e "${GREEN}项目结构创建完成!${NC}" 