#!/bin/bash

# 确保服务已启动
echo "确保代理协调器服务已在本地启动..."

# 运行基本负载测试
echo "========== 运行API响应时间测试 =========="
wrk -t8 -c100 -d60s http://localhost:3007/api/v1/sessions

# 运行高并发测试
echo "========== 运行高并发测试 =========="
wrk -t12 -c500 -d30s http://localhost:3007/api/v1/sessions

# 运行持续负载测试
echo "========== 运行持续负载测试(5分钟) =========="
wrk -t8 -c200 -d300s http://localhost:3007/api/v1/sessions
