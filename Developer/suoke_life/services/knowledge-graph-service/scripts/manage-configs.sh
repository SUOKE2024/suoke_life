#!/bin/bash

# 定义颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # 恢复默认颜色

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}  索克生活知识图谱服务配置管理脚本  ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 确保脚本从项目根目录运行
cd "$(dirname "$0")/.." || exit

# 定义命令行参数
ACTION=$1
ENV=$2
NAMESPACE=${3:-"default"}

# 显示帮助信息
show_help() {
    echo -e "${BLUE}用法:${NC}"
    echo -e "  $0 <action> <environment> [namespace]"
    echo -e ""
    echo -e "${BLUE}Actions:${NC}"
    echo -e "  create    创建ConfigMap和Secret"
    echo -e "  update    更新ConfigMap和Secret"
    echo -e "  delete    删除ConfigMap和Secret"
    echo -e "  apply     应用配置到部署"
    echo -e ""
    echo -e "${BLUE}Environments:${NC}"
    echo -e "  dev       开发环境"
    echo -e "  test      测试环境"
    echo -e "  staging   预发布环境"
    echo -e "  prod      生产环境"
    echo -e ""
    echo -e "${BLUE}Examples:${NC}"
    echo -e "  $0 create dev"
    echo -e "  $0 update prod suoke-prod"
    echo -e "  $0 apply test suoke-test"
    echo -e ""
}

# 检查参数
if [ -z "$ACTION" ] || [ -z "$ENV" ]; then
    show_help
    exit 1
fi

# 检查环境
if [[ ! "$ENV" =~ ^(dev|test|staging|prod)$ ]]; then
    echo -e "${RED}❌ 无效的环境: $ENV${NC}"
    show_help
    exit 1
fi

# 检查操作
if [[ ! "$ACTION" =~ ^(create|update|delete|apply)$ ]]; then
    echo -e "${RED}❌ 无效的操作: $ACTION${NC}"
    show_help
    exit 1
fi

# 检查kubectl是否可用
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl未安装! 请先安装kubectl${NC}"
    exit 1
fi

# 设置环境文件
ENV_FILE=".env.$ENV"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}环境文件 $ENV_FILE 不存在，使用 .env 作为备选${NC}"
    ENV_FILE=".env"
    
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}❌ 环境文件 .env 也不存在!${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}使用环境文件: $ENV_FILE${NC}"
echo -e "${BLUE}目标命名空间: $NAMESPACE${NC}"

# 创建ConfigMap
create_configmap() {
    echo -e "\n${BLUE}创建ConfigMap...${NC}"
    
    # 检查命名空间是否存在
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        echo -e "${YELLOW}命名空间 $NAMESPACE 不存在，正在创建...${NC}"
        kubectl create namespace $NAMESPACE
    fi
    
    # 创建临时配置文件
    CONFIG_FILE="config-$ENV.yaml"
    echo "# 知识图谱服务配置 - $ENV 环境" > $CONFIG_FILE
    echo "# 创建时间: $(date)" >> $CONFIG_FILE
    echo "environment: $ENV" >> $CONFIG_FILE
    
    # 从环境文件中提取非敏感配置
    grep -v "PASSWORD\|SECRET\|KEY\|TOKEN" $ENV_FILE | grep -v "^#" | grep "=" | while read -r line; do
        if [[ ! -z "$line" ]]; then
            KEY=$(echo $line | cut -d= -f1)
            VALUE=$(echo $line | cut -d= -f2-)
            echo "$KEY: \"$VALUE\"" >> $CONFIG_FILE
        fi
    done
    
    # 创建ConfigMap
    kubectl create configmap knowledge-graph-config -n $NAMESPACE --from-file=config.yaml=$CONFIG_FILE -o yaml --dry-run=client | kubectl apply -f -
    
    # 清理临时文件
    rm $CONFIG_FILE
    
    echo -e "${GREEN}✅ ConfigMap已创建${NC}"
}

# 创建Secret
create_secret() {
    echo -e "\n${BLUE}创建Secret...${NC}"
    
    # 创建临时secret文件
    SECRET_FILE="secret-$ENV.yaml"
    echo "# 知识图谱服务密钥 - $ENV 环境" > $SECRET_FILE
    echo "# 创建时间: $(date)" >> $SECRET_FILE
    
    # 从环境文件中提取敏感配置
    grep -E "PASSWORD|SECRET|KEY|TOKEN" $ENV_FILE | grep -v "^#" | grep "=" | while read -r line; do
        if [[ ! -z "$line" ]]; then
            KEY=$(echo $line | cut -d= -f1)
            VALUE=$(echo $line | cut -d= -f2-)
            echo "$KEY: \"$VALUE\"" >> $SECRET_FILE
        fi
    done
    
    # 创建Secret
    kubectl create secret generic knowledge-graph-secrets -n $NAMESPACE --from-file=secrets.yaml=$SECRET_FILE -o yaml --dry-run=client | kubectl apply -f -
    
    # 清理临时文件
    rm $SECRET_FILE
    
    echo -e "${GREEN}✅ Secret已创建${NC}"
}

# 更新ConfigMap和Secret
update_configs() {
    echo -e "\n${BLUE}更新配置...${NC}"
    
    # 删除现有ConfigMap和Secret
    kubectl delete configmap knowledge-graph-config -n $NAMESPACE --ignore-not-found
    kubectl delete secret knowledge-graph-secrets -n $NAMESPACE --ignore-not-found
    
    # 创建新的ConfigMap和Secret
    create_configmap
    create_secret
    
    echo -e "${GREEN}✅ 配置已更新${NC}"
}

# 删除ConfigMap和Secret
delete_configs() {
    echo -e "\n${BLUE}删除配置...${NC}"
    
    kubectl delete configmap knowledge-graph-config -n $NAMESPACE --ignore-not-found
    kubectl delete secret knowledge-graph-secrets -n $NAMESPACE --ignore-not-found
    
    echo -e "${GREEN}✅ 配置已删除${NC}"
}

# 应用配置到部署
apply_configs() {
    echo -e "\n${BLUE}应用配置到部署...${NC}"
    
    # 检查部署是否存在
    if ! kubectl get deployment knowledge-graph-service -n $NAMESPACE &> /dev/null; then
        echo -e "${RED}❌ 部署不存在!${NC}"
        exit 1
    fi
    
    # 更新配置
    update_configs
    
    # 重启部署以应用新配置
    kubectl rollout restart deployment knowledge-graph-service -n $NAMESPACE
    
    echo -e "${GREEN}✅ 配置已应用，部署正在重启${NC}"
    
    # 等待部署就绪
    echo -e "${YELLOW}等待部署就绪...${NC}"
    kubectl rollout status deployment/knowledge-graph-service -n $NAMESPACE --timeout=120s
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 部署已就绪${NC}"
    else
        echo -e "${RED}❌ 部署未在指定时间内就绪!${NC}"
    fi
}

# 执行操作
case $ACTION in
    create)
        create_configmap
        create_secret
        ;;
    update)
        update_configs
        ;;
    delete)
        delete_configs
        ;;
    apply)
        apply_configs
        ;;
    *)
        show_help
        exit 1
        ;;
esac

echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}✅ 操作完成!${NC}"
echo -e "${BLUE}=========================================${NC}"
