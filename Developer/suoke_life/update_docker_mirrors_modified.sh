#!/bin/bash

# 定义新的镜像加速器列表
NEW_MIRRORS=(
  "https://registry.docker-cn.com"
  "https://hub-mirror.c.163.com"
  "https://mirror.baidubce.com"
  "https://docker.mirrors.ustc.edu.cn"
)

# 检查Docker的配置文件
DOCKER_CONFIG_FILE="/etc/docker/daemon.json"

# 读取当前的配置
if [ -f "$DOCKER_CONFIG_FILE" ]; then
  echo "当前Docker配置:"
  cat "$DOCKER_CONFIG_FILE"
  
  # 读取当前配置
  CURRENT_CONFIG=$(cat "$DOCKER_CONFIG_FILE")
  
  # 检查是否已存在registry-mirrors配置
  if echo "$CURRENT_CONFIG" | grep -q "registry-mirrors"; then
    echo "更新现有的registry-mirrors配置..."
    
    # 提取现有镜像
    EXISTING_MIRRORS=$(cat "$DOCKER_CONFIG_FILE" | grep -o '"https://[^"]*"' | tr -d '"')
    
    echo "现有的镜像加速器:"
    for mirror in $EXISTING_MIRRORS; do
      echo "  - $mirror"
    done
    
    # 构建新的配置文件内容
    echo "新增的镜像加速器:"
    for mirror in "${NEW_MIRRORS[@]}"; do
      echo "  - $mirror"
    done
    
    # 合并所有镜像（现有的和新的）
    ALL_MIRRORS=($EXISTING_MIRRORS "${NEW_MIRRORS[@]}")
    
    # 去重
    UNIQUE_MIRRORS=($(echo "${ALL_MIRRORS[@]}" | tr ' ' '\n' | sort -u))
    
    # 构建新的镜像JSON数组部分
    MIRRORS_JSON=""
    for ((i=0; i<${#UNIQUE_MIRRORS[@]}; i++)); do
      if [ $i -eq $((${#UNIQUE_MIRRORS[@]}-1)) ]; then
        MIRRORS_JSON="${MIRRORS_JSON}    \"${UNIQUE_MIRRORS[$i]}\""
      else
        MIRRORS_JSON="${MIRRORS_JSON}    \"${UNIQUE_MIRRORS[$i]}\",\n"
      fi
    done
    
    # 构建完整的JSON配置
    DNS_PART=$(echo "$CURRENT_CONFIG" | grep -o '"dns":\s*\[[^]]*\]')
    if [ -n "$DNS_PART" ]; then
      NEW_CONFIG="{\n  \"registry-mirrors\": [\n${MIRRORS_JSON}\n  ],\n  ${DNS_PART}\n}"
    else
      NEW_CONFIG="{\n  \"registry-mirrors\": [\n${MIRRORS_JSON}\n  ]\n}"
    fi
    
    # 输出新的配置
    echo "新的Docker配置:"
    echo -e "$NEW_CONFIG"
  else
    echo "添加新的registry-mirrors配置..."
    
    # 检查是否有其他配置项
    if [ $(echo "$CURRENT_CONFIG" | grep -v '^{\s*$' | grep -v '^\s*}\s*$' | wc -l) -gt 0 ]; then
      # 有其他配置项，添加registry-mirrors
      # 移除最后的花括号
      CONFIG_WITHOUT_CLOSING=$(echo "$CURRENT_CONFIG" | sed 's/}\s*$//')
      
      # 检查是否需要添加逗号
      if ! echo "$CONFIG_WITHOUT_CLOSING" | grep -q ',\s*$'; then
        CONFIG_WITHOUT_CLOSING="${CONFIG_WITHOUT_CLOSING},"
      fi
      
      # 添加registry-mirrors配置
      MIRRORS_JSON=""
      for ((i=0; i<${#NEW_MIRRORS[@]}; i++)); do
        if [ $i -eq $((${#NEW_MIRRORS[@]}-1)) ]; then
          MIRRORS_JSON="${MIRRORS_JSON}    \"${NEW_MIRRORS[$i]}\""
        else
          MIRRORS_JSON="${MIRRORS_JSON}    \"${NEW_MIRRORS[$i]}\",\n"
        fi
      done
      
      NEW_CONFIG="${CONFIG_WITHOUT_CLOSING}\n  \"registry-mirrors\": [\n${MIRRORS_JSON}\n  ]\n}"
    else
      # 没有其他配置项，创建新的配置
      MIRRORS_JSON=""
      for ((i=0; i<${#NEW_MIRRORS[@]}; i++)); do
        if [ $i -eq $((${#NEW_MIRRORS[@]}-1)) ]; then
          MIRRORS_JSON="${MIRRORS_JSON}    \"${NEW_MIRRORS[$i]}\""
        else
          MIRRORS_JSON="${MIRRORS_JSON}    \"${NEW_MIRRORS[$i]}\",\n"
        fi
      done
      
      NEW_CONFIG="{\n  \"registry-mirrors\": [\n${MIRRORS_JSON}\n  ]\n}"
    fi
    
    # 输出新的配置
    echo "新的Docker配置:"
    echo -e "$NEW_CONFIG"
  fi
else
  echo "Docker配置文件不存在，创建新的配置内容..."
  
  # 创建新的配置内容
  MIRRORS_JSON=""
  for ((i=0; i<${#NEW_MIRRORS[@]}; i++)); do
    if [ $i -eq $((${#NEW_MIRRORS[@]}-1)) ]; then
      MIRRORS_JSON="${MIRRORS_JSON}    \"${NEW_MIRRORS[$i]}\""
    else
      MIRRORS_JSON="${MIRRORS_JSON}    \"${NEW_MIRRORS[$i]}\",\n"
    fi
  done
  
  NEW_CONFIG="{\n  \"registry-mirrors\": [\n${MIRRORS_JSON}\n  ]\n}"
  
  # 输出新的配置
  echo "新的Docker配置:"
  echo -e "$NEW_CONFIG"
fi

echo ""
echo "要应用此配置，请将以上JSON内容写入 /etc/docker/daemon.json 文件"
echo "执行以下命令："
echo "sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.bak  # 备份当前配置"
echo "sudo bash -c 'cat > /etc/docker/daemon.json << EOF"
echo -e "$NEW_CONFIG"
echo "EOF'"
echo "sudo systemctl restart docker  # 或 sudo service docker restart"
echo ""
echo "测试镜像加速器的方法:"
echo "1. 更新Docker配置后重启Docker服务"
echo "2. 执行: docker pull hello-world"
echo "3. 检查拉取速度和是否成功"
