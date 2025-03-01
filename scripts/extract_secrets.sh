#!/bin/bash

# extract_secrets.sh - GitHub Actions 密钥提取脚本
#
# 此脚本从本地项目目录中提取 GitHub Actions 所需的密钥和环境变量，
# 并准备好可以直接添加到 GitHub 仓库密钥的格式。
#
# 使用方法:
#   cd /Users/songxu/Developer/suoke_life
#   ./scripts/extract_secrets.sh

set -e  # 遇到错误立即退出

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 创建输出目录
OUTPUT_DIR="github_secrets"
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}开始从项目中提取密钥和环境变量...${NC}"

# 1. 提取 Android 签名密钥
extract_android_signing_key() {
  echo -e "${YELLOW}提取 Android 签名密钥...${NC}"
  
  # 检查 keystore 文件是否存在
  if [ -f "android/app/keystore/release.keystore" ]; then
    KEYSTORE_PATH="android/app/keystore/release.keystore"
  elif [ -f "android/app/keystore/upload-keystore.jks" ]; then
    KEYSTORE_PATH="android/app/keystore/upload-keystore.jks"
  elif [ -f "android/app/upload-keystore.jks" ]; then
    KEYSTORE_PATH="android/app/upload-keystore.jks"
  elif [ -f "android/app/debug.keystore" ]; then
    KEYSTORE_PATH="android/app/debug.keystore"
    echo -e "${YELLOW}警告: 只找到调试密钥库，不推荐用于生产环境${NC}"
  else
    echo -e "${RED}错误: 未找到 Android 签名密钥库${NC}"
    return 1
  fi
  
  # 将 keystore 转换为 base64
  base64 "$KEYSTORE_PATH" > "$OUTPUT_DIR/KEYSTORE_JKS_BASE64.txt"
  echo -e "${GREEN}已将 Android 签名密钥库转换为 Base64 格式: $OUTPUT_DIR/KEYSTORE_JKS_BASE64.txt${NC}"
  
  # 提取 key.properties
  if [ -f "android/key.properties" ]; then
    cp "android/key.properties" "$OUTPUT_DIR/KEY_PROPERTIES.txt"
    echo -e "${GREEN}已复制 Android 签名配置: $OUTPUT_DIR/KEY_PROPERTIES.txt${NC}"
  else
    echo -e "${YELLOW}警告: 未找到 android/key.properties 文件${NC}"
    
    # 创建示例 key.properties
    cat > "$OUTPUT_DIR/KEY_PROPERTIES.txt" << EOL
storePassword=您的密钥库密码
keyPassword=您的密钥密码
keyAlias=您的密钥别名
storeFile=../app/upload-keystore.jks
EOL
    echo -e "${YELLOW}已创建示例 key.properties 文件，请填写正确的值: $OUTPUT_DIR/KEY_PROPERTIES.txt${NC}"
  fi
}

# 2. 提取 iOS 签名证书和配置文件
extract_ios_signing() {
  echo -e "${YELLOW}提取 iOS 签名证书和配置文件...${NC}"
  
  # 检查常见的 iOS 证书和配置文件位置
  P12_PATH=""
  PROFILE_PATH=""
  
  # 检查常见位置的证书
  for path in "ios/certs" "ios/certificates" "ios/signing" "ios"; do
    if [ -d "$path" ]; then
      # 查找 .p12 文件
      P12_FILES=$(find "$path" -name "*.p12" 2>/dev/null)
      if [ -n "$P12_FILES" ]; then
        P12_PATH=$(echo "$P12_FILES" | head -n 1)
        break
      fi
    fi
  done
  
  # 检查配置文件
  for path in "ios/certs" "ios/profiles" "ios"; do
    if [ -d "$path" ]; then
      # 查找 .mobileprovision 文件
      PROFILE_FILES=$(find "$path" -name "*.mobileprovision" 2>/dev/null)
      if [ -n "$PROFILE_FILES" ]; then
        PROFILE_PATH=$(echo "$PROFILE_FILES" | head -n 1)
        break
      fi
    fi
  done
  
  # 转换证书为 Base64
  if [ -n "$P12_PATH" ]; then
    base64 "$P12_PATH" > "$OUTPUT_DIR/P12_BASE64.txt"
    echo -e "${GREEN}已将 iOS 签名证书转换为 Base64 格式: $OUTPUT_DIR/P12_BASE64.txt${NC}"
    
    # 创建密码提示文件
    echo "请在此填入您的 P12 证书密码" > "$OUTPUT_DIR/P12_PASSWORD.txt"
    echo -e "${YELLOW}请编辑文件并填入您的 P12 证书密码: $OUTPUT_DIR/P12_PASSWORD.txt${NC}"
  else
    echo -e "${YELLOW}未找到 iOS 签名证书 (.p12)${NC}"
  fi
  
  # 转换配置文件为 Base64
  if [ -n "$PROFILE_PATH" ]; then
    base64 "$PROFILE_PATH" > "$OUTPUT_DIR/PROVISIONING_PROFILE_BASE64.txt"
    echo -e "${GREEN}已将 iOS 配置文件转换为 Base64 格式: $OUTPUT_DIR/PROVISIONING_PROFILE_BASE64.txt${NC}"
  else
    echo -e "${YELLOW}未找到 iOS 配置文件 (.mobileprovision)${NC}"
  fi
}

# 3. 提取服务器部署配置
extract_server_config() {
  echo -e "${YELLOW}提取服务器部署配置...${NC}"
  
  # 创建阿里云服务器配置
  echo "118.31.223.213" > "$OUTPUT_DIR/ALIYUN_HOST.txt"
  echo "root" > "$OUTPUT_DIR/ALIYUN_USERNAME.txt"
  
  # 提取 SSH 密钥
  SSH_KEY_PATH="$HOME/.ssh/id_rsa"
  if [ -f "$SSH_KEY_PATH" ]; then
    cat "$SSH_KEY_PATH" > "$OUTPUT_DIR/ALIYUN_SSH_KEY.txt"
    echo -e "${GREEN}已复制 SSH 私钥: $OUTPUT_DIR/ALIYUN_SSH_KEY.txt${NC}"
  else
    echo -e "${YELLOW}未找到默认 SSH 私钥，请手动提供服务器 SSH 密钥${NC}"
    echo "请将您的 SSH 私钥粘贴到此处" > "$OUTPUT_DIR/ALIYUN_SSH_KEY.txt"
  fi
}

# 4. 提取应用商店部署配置
extract_store_config() {
  echo -e "${YELLOW}提取应用商店部署配置...${NC}"
  
  # 检查 Google Play 服务账号
  GOOGLE_PLAY_JSON_PATH=""
  for path in "android/fastlane" "android/certs" "android" "."; do
    for file in "$path/google-play-service-account.json" "$path/service-account.json" "$path/play-store-service-account.json"; do
      if [ -f "$file" ]; then
        GOOGLE_PLAY_JSON_PATH="$file"
        break 2
      fi
    done
  done
  
  if [ -n "$GOOGLE_PLAY_JSON_PATH" ]; then
    cat "$GOOGLE_PLAY_JSON_PATH" > "$OUTPUT_DIR/GOOGLE_PLAY_SERVICE_ACCOUNT.txt"
    echo -e "${GREEN}已复制 Google Play 服务账号: $OUTPUT_DIR/GOOGLE_PLAY_SERVICE_ACCOUNT.txt${NC}"
  else
    echo -e "${YELLOW}未找到 Google Play 服务账号 JSON 文件${NC}"
    echo "请将您的 Google Play 服务账号 JSON 粘贴到此处" > "$OUTPUT_DIR/GOOGLE_PLAY_SERVICE_ACCOUNT.txt"
  fi
  
  # 创建 App Store Connect API 配置占位文件
  echo "请将您的 App Store Connect API 密钥粘贴到此处" > "$OUTPUT_DIR/APPSTORE_API_KEY.txt"
  echo "请将您的 App Store Connect API 密钥 ID 粘贴到此处" > "$OUTPUT_DIR/APPSTORE_API_KEY_ID.txt"
  echo "请将您的 App Store Connect API 密钥发行者 ID 粘贴到此处" > "$OUTPUT_DIR/APPSTORE_API_KEY_ISSUER_ID.txt"
  
  echo -e "${YELLOW}已创建 App Store Connect API 密钥占位文件，请手动填入正确的值${NC}"
}

# 5. 生成密钥添加指南
generate_guide() {
  echo -e "${YELLOW}生成密钥添加指南...${NC}"
  
  README_PATH="$OUTPUT_DIR/README.md"
  
  cat > "$README_PATH" << EOL
# GitHub Actions 密钥设置指南

本文件包含了设置 GitHub Actions 所需密钥的步骤。

## 如何添加密钥到 GitHub 仓库

1. 打开 GitHub 仓库页面
2. 点击 "Settings" > "Secrets and variables" > "Actions"
3. 点击 "New repository secret"
4. 按照下面的说明添加每个密钥

## 密钥列表

以下是所有需要添加的密钥：

### Android 构建密钥

- **KEYSTORE_JKS_BASE64**: Android 签名密钥库的 Base64 编码
  - 从 \`KEYSTORE_JKS_BASE64.txt\` 复制内容
  
- **KEY_PROPERTIES**: Android 签名配置
  - 从 \`KEY_PROPERTIES.txt\` 复制内容

### iOS 构建密钥

- **P12_BASE64**: iOS 签名证书的 Base64 编码
  - 从 \`P12_BASE64.txt\` 复制内容
  
- **P12_PASSWORD**: iOS 证书密码
  - 从 \`P12_PASSWORD.txt\` 复制内容
  
- **PROVISIONING_PROFILE_BASE64**: iOS 配置文件的 Base64 编码
  - 从 \`PROVISIONING_PROFILE_BASE64.txt\` 复制内容

### 服务器部署密钥

- **ALIYUN_HOST**: 阿里云服务器 IP 地址
  - 从 \`ALIYUN_HOST.txt\` 复制内容
  
- **ALIYUN_USERNAME**: 阿里云服务器用户名
  - 从 \`ALIYUN_USERNAME.txt\` 复制内容
  
- **ALIYUN_SSH_KEY**: 阿里云服务器 SSH 私钥
  - 从 \`ALIYUN_SSH_KEY.txt\` 复制内容

### 应用商店部署密钥

- **GOOGLE_PLAY_SERVICE_ACCOUNT**: Google Play 服务账号 JSON
  - 从 \`GOOGLE_PLAY_SERVICE_ACCOUNT.txt\` 复制内容
  
- **APPSTORE_API_KEY**: App Store Connect API 密钥
  - 从 \`APPSTORE_API_KEY.txt\` 复制内容
  
- **APPSTORE_API_KEY_ID**: App Store Connect API 密钥 ID
  - 从 \`APPSTORE_API_KEY_ID.txt\` 复制内容
  
- **APPSTORE_API_KEY_ISSUER_ID**: App Store Connect API 密钥发行者 ID
  - 从 \`APPSTORE_API_KEY_ISSUER_ID.txt\` 复制内容

## 注意事项

- 所有密钥内容都应该保密，不要将其提交到代码仓库
- 某些密钥文件可能需要手动填写内容
- 密钥添加后，GitHub 将不再显示其内容，所以请保存好原始文件
EOL
  
  echo -e "${GREEN}已生成密钥添加指南: $README_PATH${NC}"
}

# 执行提取函数
extract_android_signing_key || true
extract_ios_signing || true
extract_server_config || true
extract_store_config || true
generate_guide

echo -e "${GREEN}所有密钥和环境变量提取完成！${NC}"
echo -e "${GREEN}结果保存在 $OUTPUT_DIR 目录中${NC}"
echo -e "${BLUE}请按照 $OUTPUT_DIR/README.md 的说明将密钥添加到 GitHub 仓库${NC}" 