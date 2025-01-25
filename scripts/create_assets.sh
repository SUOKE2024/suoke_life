#!/bin/bash

# 创建资源目录
mkdir -p assets/images
mkdir -p assets/icons
mkdir -p assets/config

# 创建示例配置文件
cat > assets/config/app_config.json << EOL
{
  "api": {
    "baseUrl": "https://api.suoke.com",
    "timeout": 30000
  },
  "features": {
    "enableBiometrics": true,
    "enablePushNotifications": true,
    "enableOfflineMode": true
  }
}
EOL

# 创建 .gitkeep 文件以保持目录结构
touch assets/images/.gitkeep
touch assets/icons/.gitkeep

echo "资源目录结构已创建" 