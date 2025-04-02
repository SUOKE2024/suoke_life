#!/bin/bash
# VPC隧道设置脚本
# 功能：在主服务器和K8s集群服务器之间建立安全通信隧道
# 版本：1.0
# 更新日期：2024-03-22

# 配置参数
MAIN_SERVER="118.31.223.213"
K8S_SERVER="120.26.161.52"
TUNNEL_PORT=22222
SSH_PORT=22
TUNNEL_USER="tunnel"
LOG_FILE="/var/log/vpc_tunnel.log"
TUNNEL_INTERFACE="tun0"
TUNNEL_LOCAL_IP="192.168.100.1"
TUNNEL_REMOTE_IP="192.168.100.2"

# 创建日志文件
touch $LOG_FILE

# 日志函数
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 创建隧道用户
create_tunnel_user() {
    log_message "检查隧道用户是否存在..."
    if id "$TUNNEL_USER" &>/dev/null; then
        log_message "隧道用户 $TUNNEL_USER 已存在"
    else
        log_message "创建隧道用户 $TUNNEL_USER..."
        useradd -m -s /bin/bash $TUNNEL_USER
        echo "$TUNNEL_USER:$(openssl rand -base64 12)" | chpasswd
        mkdir -p /home/$TUNNEL_USER/.ssh
        chmod 700 /home/$TUNNEL_USER/.ssh
        touch /home/$TUNNEL_USER/.ssh/authorized_keys
        chmod 600 /home/$TUNNEL_USER/.ssh/authorized_keys
        chown -R $TUNNEL_USER:$TUNNEL_USER /home/$TUNNEL_USER/.ssh
        log_message "隧道用户创建完成"
    fi
}

# 生成SSH密钥
generate_ssh_key() {
    log_message "检查SSH密钥是否存在..."
    if [ ! -f "/home/$TUNNEL_USER/.ssh/id_rsa" ]; then
        log_message "生成SSH密钥..."
        su - $TUNNEL_USER -c "ssh-keygen -t rsa -b 4096 -f /home/$TUNNEL_USER/.ssh/id_rsa -N ''"
        log_message "SSH密钥生成完成"
    else
        log_message "SSH密钥已存在"
    fi
}

# 设置SSH配置
setup_ssh_config() {
    log_message "配置SSH客户端..."
    cat > /home/$TUNNEL_USER/.ssh/config << EOF
Host k8s
    HostName $K8S_SERVER
    User $TUNNEL_USER
    Port $SSH_PORT
    IdentityFile /home/$TUNNEL_USER/.ssh/id_rsa
    ServerAliveInterval 30
    ServerAliveCountMax 3
EOF
    chmod 600 /home/$TUNNEL_USER/.ssh/config
    chown $TUNNEL_USER:$TUNNEL_USER /home/$TUNNEL_USER/.ssh/config
    log_message "SSH配置完成"
}

# 检查是否已安装必要工具
check_dependencies() {
    log_message "检查依赖工具..."
    packages=("openssh-server" "autossh" "net-tools" "iptables" "iproute2")
    
    for pkg in "${packages[@]}"; do
        if command -v $pkg >/dev/null 2>&1 || rpm -q $pkg >/dev/null 2>&1 || dpkg -l $pkg >/dev/null 2>&1; then
            log_message "$pkg 已安装"
        else
            log_message "安装 $pkg..."
            if [ -x "$(command -v apt-get)" ]; then
                apt-get update && apt-get install -y $pkg
            elif [ -x "$(command -v yum)" ]; then
                yum install -y $pkg
            else
                log_message "无法安装 $pkg，请手动安装"
                exit 1
            fi
        fi
    done
    
    log_message "依赖检查完成"
}

# 设置防火墙规则
setup_firewall() {
    log_message "配置防火墙规则..."
    
    # 允许SSH连接
    iptables -A INPUT -p tcp --dport $SSH_PORT -j ACCEPT
    
    # 允许VPN隧道流量
    iptables -A INPUT -i $TUNNEL_INTERFACE -j ACCEPT
    iptables -A FORWARD -i $TUNNEL_INTERFACE -j ACCEPT
    iptables -A FORWARD -o $TUNNEL_INTERFACE -j ACCEPT
    
    # 保存防火墙规则
    if [ -x "$(command -v iptables-save)" ]; then
        iptables-save > /etc/iptables/rules.v4
        log_message "防火墙规则已保存"
    else
        log_message "iptables-save命令不可用，无法持久化防火墙规则"
    fi
}

# 设置VPN隧道
setup_vpn() {
    log_message "设置VPN隧道..."
    
    # 创建TUN接口
    ip tuntap add dev $TUNNEL_INTERFACE mode tun
    ip addr add $TUNNEL_LOCAL_IP/30 dev $TUNNEL_INTERFACE
    ip link set dev $TUNNEL_INTERFACE up
    
    log_message "VPN隧道设置完成，本地IP: $TUNNEL_LOCAL_IP"
}

# 建立与远程服务器的连接
connect_remote() {
    log_message "尝试与远程服务器建立连接..."
    
    # 使用SSH隧道连接远程服务器
    cmd="ssh -f -N -w 0:0 -o ServerAliveInterval=30 -o ServerAliveCountMax=3 k8s"
    su - $TUNNEL_USER -c "$cmd"
    
    if [ $? -eq 0 ]; then
        log_message "SSH隧道连接成功"
    else
        log_message "SSH隧道连接失败，请检查网络和认证设置"
        exit 1
    fi
}

# 设置永久隧道服务
setup_tunnel_service() {
    log_message "创建永久隧道服务..."
    
    cat > /etc/systemd/system/vpc-tunnel.service << EOF
[Unit]
Description=VPC Tunnel Service
After=network.target

[Service]
User=$TUNNEL_USER
ExecStart=/usr/bin/autossh -M 0 -N -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -w 0:0 k8s
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable vpc-tunnel.service
    systemctl start vpc-tunnel.service
    
    log_message "永久隧道服务已启动"
}

# 设置路由
setup_routes() {
    log_message "设置路由..."
    
    # 添加到K8s服务的路由
    ip route add $K8S_SERVER via $TUNNEL_REMOTE_IP dev $TUNNEL_INTERFACE
    
    # 添加到K8s集群内部网络的路由
    # 注意：这里需要修改为实际的K8s集群内部网络
    # ip route add 172.16.0.0/16 via $TUNNEL_REMOTE_IP dev $TUNNEL_INTERFACE
    
    log_message "路由设置完成"
}

# 测试连接
test_connection() {
    log_message "测试VPC隧道连接..."
    
    if ping -c 3 $TUNNEL_REMOTE_IP > /dev/null 2>&1; then
        log_message "VPC隧道连接测试成功！"
        log_message "隧道IP连通性：$(ping -c 1 -W 2 $TUNNEL_REMOTE_IP | grep 'bytes from')"
        
        # 测试到K8s服务器的连接
        if ping -c 3 $K8S_SERVER > /dev/null 2>&1; then
            log_message "K8s服务器连通性测试成功！"
            log_message "K8s服务器连通性：$(ping -c 1 -W 2 $K8S_SERVER | grep 'bytes from')"
        else
            log_message "K8s服务器连通性测试失败，请检查路由设置"
        fi
    else
        log_message "VPC隧道连接测试失败，请检查隧道设置"
    fi
}

# 显示使用帮助
show_help() {
    echo "VPC隧道设置脚本"
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help       显示此帮助信息"
    echo "  -s, --setup      设置VPC隧道"
    echo "  -t, --test       测试隧道连接"
    echo "  -r, --restart    重启隧道服务"
    echo "  -d, --down       关闭隧道"
    echo ""
}

# 主函数
main() {
    case "$1" in
        -h|--help)
            show_help
            ;;
        -s|--setup)
            log_message "开始设置VPC隧道..."
            check_dependencies
            create_tunnel_user
            generate_ssh_key
            setup_ssh_config
            setup_firewall
            setup_vpn
            connect_remote
            setup_tunnel_service
            setup_routes
            test_connection
            log_message "VPC隧道设置完成"
            ;;
        -t|--test)
            test_connection
            ;;
        -r|--restart)
            log_message "重启VPC隧道服务..."
            systemctl restart vpc-tunnel.service
            sleep 5
            test_connection
            ;;
        -d|--down)
            log_message "关闭VPC隧道..."
            systemctl stop vpc-tunnel.service
            ip link set dev $TUNNEL_INTERFACE down
            ip tuntap del dev $TUNNEL_INTERFACE mode tun
            log_message "VPC隧道已关闭"
            ;;
        *)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@" 