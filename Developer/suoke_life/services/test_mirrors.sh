#!/bin/bash

test_mirror() {
  local mirror=$1
  echo "测试镜像: $mirror"
  time curl -s -o /dev/null -w "%{http_code}
" "$mirror/v2/" || echo "连接失败"
  echo ""
}

echo "开始测试Docker registry镜像..."
echo "===================================="

test_mirror "https://registry.docker-cn.com"
test_mirror "https://hub-mirror.c.163.com"
test_mirror "https://mirror.baidubce.com"
test_mirror "https://docker.mirrors.ustc.edu.cn"

echo "===================================="
echo "测试完成"
