#!/bin/bash

# 设置环境变量
export API_GATEWAY_ENABLED=true
export API_GATEWAY_NAME=api-gateway
export API_BASE_PATH=/api
export TRUSTED_HEADERS=X-API-Gateway,X-Request-ID,Authorization
export VAULT_ENABLED=true
export VAULT_ENDPOINT=http://localhost:8200
export VAULT_PATH=secret/data/api-gateway

# 启动本地开发环境
echo "正在启动API网关开发环境..."
npm run dev