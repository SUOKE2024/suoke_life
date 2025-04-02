#!/bin/bash

# 定义颜色代码
YELLOW='\033[1;33m'
GREEN='\033[1;32m'
RED='\033[1;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}开始安装Swagger文档依赖...${NC}"

# 安装主要依赖
npm install --save swagger-jsdoc swagger-ui-express express-basic-auth
echo -e "${GREEN}主要依赖安装完成!${NC}"

# 安装类型定义
npm install --save-dev @types/swagger-jsdoc @types/swagger-ui-express
echo -e "${GREEN}TypeScript类型定义安装完成!${NC}"

# 确保配置文件目录存在
if [ ! -d "src/config" ]; then
  mkdir -p src/config
  echo -e "${YELLOW}创建了配置文件目录${NC}"
fi

echo -e "${GREEN}Swagger文档依赖安装完成!${NC}"
echo -e "${YELLOW}请确保在服务启动脚本中添加了Swagger文档的初始化代码${NC}"
echo -e "${YELLOW}API文档可在服务启动后通过 http://localhost:3007/api-docs 访问${NC}"