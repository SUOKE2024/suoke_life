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
  
  # 创建备份
  sudo cp "$DOCKER_CONFIG_FILE" "${DOCKER_CONFIG_FILE}.bak"
  echo "已创建配置备份: ${DOCKER_CONFIG_FILE}.bak"
  
  # 读取当前配置
  CURRENT_CONFIG=$(cat "$DOCKER_CONFIG_FILE")
  
  # 检查是否已存在registry-mirrors配置
  if echo "$CURRENT_CONFIG" | grep -q "registry-mirrors"; then
    echo "更新现有的registry-mirrors配置..."
    
    # 使用临时文件
    TMP_FILE=$(mktemp)
    
    # 提取和保留现有镜像
    EXISTING_MIRRORS=$(echo "$CURRENT_CONFIG" | grep -o '"registry-mirrors":\s*\[[^]]*\]' | grep -o 'https://[^"]*')
    
    # 合并现有镜像和新镜像，去重
    ALL_MIRRORS=("$EXISTING_MIRRORS" "${NEW_MIRRORS[@]}")
    UNIQUE_MIRRORS=$(echo "${ALL_MIRRORS[@]}" | tr ' ' '\n' | sort -u | grep -v '^$')
    
    # 构建新的镜像JSON数组
    MIRRORS_JSON="\"registry-mirrors\": ["
    for mirror in $UNIQUE_MIRRORS; do
      MIRRORS_JSON="$MIRRORS_JSON\"$mirror\", "
    done
    # 移除最后的逗号和空格
    MIRRORS_JSON=${MIRRORS_JSON%, }
    MIRRORS_JSON="$MIRRORS_JSON]"
    
    # 替换现有的registry-mirrors部分
    echo "$CURRENT_CONFIG" | sed "s/\"registry-mirrors\":\s*\[[^]]*\]/$MIRRORS_JSON/" > "$TMP_FILE"
    
    # 使用sudo权限写入配置文件
    sudo cp "$TMP_FILE" "$DOCKER_CONFIG_FILE"
    rm "$TMP_FILE"
  else
    echo "添加新的registry-mirrors配置..."
    
    # 没有找到registry-mirrors，创建一个新的
    TMP_FILE=$(mktemp)
    
    # 移除最后的花括号
    echo "$CURRENT_CONFIG" | sed 's/}$//' > "$TMP_FILE"
    
    # 检查是否需要添加逗号
    if grep -q '[^{,]\s*$' "$TMP_FILE"; then
      echo "," >> "$TMP_FILE"
    fi
    
    # 添加registry-mirrors配置
    echo "  \"registry-mirrors\": [" >> "$TMP_FILE"
    for ((i=0; i<${#NEW_MIRRORS[@]}; i++)); do
      if [ $i -eq $((${#NEW_MIRRORS[@]}-1)) ]; then
        echo "    \"${NEW_MIRRORS[$i]}\"" >> "$TMP_FILE"
      else
        echo "    \"${NEW_MIRRORS[$i]}\"," >> "$TMP_FILE"
      fi
    done
    echo "  ]" >> "$TMP_FILE"
    echo "}" >> "$TMP_FILE"
    
    # 使用sudo权限写入配置文件
    sudo cp "$TMP_FILE" "$DOCKER_CONFIG_FILE"
    rm "$TMP_FILE"
  fi
else
  echo "Docker配置文件不存在，创建新的配置文件..."
  
  # 创建目录
  sudo mkdir -p /etc/docker
  
  # 创建新的配置文件
  TMP_FILE=$(mktemp)
  echo "{" >> "$TMP_FILE"
  echo "  \"registry-mirrors\": [" >> "$TMP_FILE"
  for ((i=0; i<${#NEW_MIRRORS[@]}; i++)); do
    if [ $i -eq $((${#NEW_MIRRORS[@]}-1)) ]; then
      echo "    \"${NEW_MIRRORS[$i]}\"" >> "$TMP_FILE"
    else
      echo "    \"${NEW_MIRRORS[$i]}\"," >> "$TMP_FILE"
    fi
  done
  echo "  ]" >> "$TMP_FILE"
  echo "}" >> "$TMP_FILE"
  
  # 使用sudo权限写入配置文件
  sudo cp "$TMP_FILE" "$DOCKER_CONFIG_FILE"
  rm "$TMP_FILE"
fi

echo "已更新Docker镜像加速器配置"
echo "重启Docker服务以使配置生效"
echo "执行: sudo systemctl restart docker"
