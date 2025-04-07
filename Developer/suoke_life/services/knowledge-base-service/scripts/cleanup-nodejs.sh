#!/bin/bash

# 清理Node.js相关文件脚本
echo "开始清理Node.js相关文件..."

# 删除Node.js源代码文件夹
rm -rf src/
rm -rf node_modules/

# 删除Node.js配置文件
rm -f package.json
rm -f package-lock.json
rm -f tsconfig.json
rm -f jest.config.js
rm -f nodemon.json
rm -f .eslintrc.js
rm -f .prettierrc

# 删除Node.js测试目录
rm -rf test/

# 保留其他可能有用的目录，如文档、配置等

echo "Node.js相关文件清理完成" 