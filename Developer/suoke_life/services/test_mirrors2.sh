#!/bin/bash

test_mirror() {
  local mirror=$1
  echo "测试镜像: $mirror"
  curl -s -m 5 -o /dev/null -w "HTTP状态码: %{http_code}, 时间: %{time_total}秒
" "$mirror" || echo "连接失败"
  echo ""
}

echo "开始测试Docker registry镜像..."
echo "===================================="

test_mirror "https://registry.docker-cn.com"
test_mirror "https://hub-mirror.c.163.com"
test_mirror "https://mirror.baidubce.com"
test_mirror "https://docker.mirrors.ustc.edu.cn"
test_mirror "https://registry.hub.docker.com"
test_mirror "https://docker.io"

echo "===================================="
echo "测试完成"
