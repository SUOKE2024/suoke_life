#!/bin/bash

# 安装开发依赖
echo "正在安装开发依赖..."

# 安装Node.js类型定义
npm install --save-dev @types/node

# 安装Express类型定义
npm install --save-dev @types/express

# 安装Axios类型定义
npm install --save-dev @types/axios

# 安装Jest类型定义
npm install --save-dev @types/jest

# 安装UUID类型定义
npm install --save-dev @types/uuid

# 安装CORS类型定义
npm install --save-dev @types/cors

# 设置脚本执行权限
chmod +x scripts/*.sh

echo "开发依赖安装完成!" 