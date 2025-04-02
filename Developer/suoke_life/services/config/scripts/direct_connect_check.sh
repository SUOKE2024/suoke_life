#!/bin/bash
# 阿里云VPC直连诊断工具
# 功能：检查和诊断阿里云VPC之间的连接问题
# 版本：1.0
# 更新日期：2024-03-22

# 配置
MAIN_SERVER="118.31.223.213"
K8S_SERVER="120.26.161.52"
LOG_FILE="/var/log/vpc_diagnostic.log"
HTTP_PORT=80
SSH_PORT=22
ICMP_COUNT=5
TIMEOUT=3
VPC_SERVICES=("ecs" "cen" "vpc" "nat")

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 创建日志文件
touch $LOG_FILE

# 日志函数
log_message() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 标题显示
show_header() {
    clear
    echo -e "${BLUE}=======================================================${NC}"
    echo -e "${BLUE}           阿里云VPC直连诊断工具 v1.0                  ${NC}"
    echo -e "${BLUE}=======================================================${NC}"
    echo ""
}

# 检查基本连接
check_basic_connectivity() {
    log_message "${YELLOW}正在检查基本网络连接...${NC}"
    
    # ICMP连接检查
    log_message "ICMP检查 (ping): $K8S_SERVER"
    if ping -c $ICMP_COUNT -W $TIMEOUT $K8S_SERVER > /dev/null 2>&1; then
        log_message "${GREEN}✓ ICMP连接正常${NC}"
        icmp_status="${GREEN}正常${NC}"
    else
        log_message "${RED}✗ ICMP连接失败${NC}"
        icmp_status="${RED}失败${NC}"
    fi
    
    # TCP连接检查 (SSH)
    log_message "TCP检查 (SSH端口 $SSH_PORT): $K8S_SERVER"
    if nc -z -w $TIMEOUT $K8S_SERVER $SSH_PORT > /dev/null 2>&1; then
        log_message "${GREEN}✓ SSH端口连接正常${NC}"
        ssh_status="${GREEN}正常${NC}"
    else
        log_message "${RED}✗ SSH端口连接失败${NC}"
        ssh_status="${RED}失败${NC}"
    fi
    
    # TCP连接检查 (HTTP)
    log_message "TCP检查 (HTTP端口 $HTTP_PORT): $K8S_SERVER"
    if nc -z -w $TIMEOUT $K8S_SERVER $HTTP_PORT > /dev/null 2>&1; then
        log_message "${GREEN}✓ HTTP端口连接正常${NC}"
        http_status="${GREEN}正常${NC}"
    else
        log_message "${RED}✗ HTTP端口连接失败${NC}"
        http_status="${RED}失败${NC}"
    fi
    
    # 显示结果
    echo -e "\n====== 基本连接检查结果 ======\n"
    echo -e "ICMP检查 (ping): $icmp_status"
    echo -e "TCP检查 (SSH端口): $ssh_status"
    echo -e "TCP检查 (HTTP端口): $http_status"
    echo -e "\n=============================="
}

# 检查路由
check_routing() {
    log_message "${YELLOW}正在检查路由信息...${NC}"
    
    echo -e "\n====== 路由检查 ======\n"
    
    # 获取路由表
    route_info=$(ip route get $K8S_SERVER 2>&1)
    log_message "路由信息: $route_info"
    echo -e "路由信息: $route_info"
    
    # traceroute检查
    log_message "执行traceroute: $K8S_SERVER"
    echo -e "\n执行traceroute:\n"
    traceroute -n -w 2 -m 15 $K8S_SERVER
    
    echo -e "\n=============================="
}

# MTU检查
check_mtu() {
    log_message "${YELLOW}正在检查MTU设置...${NC}"
    
    echo -e "\n====== MTU检查 ======\n"
    
    # 获取接口信息
    interface=$(ip route get $K8S_SERVER | grep -oP '(?<=dev )[^ ]+')
    mtu=$(ip link show $interface | grep -oP '(?<=mtu )[0-9]+')
    
    log_message "接口: $interface, MTU: $mtu"
    echo -e "接口: $interface, MTU: $mtu"
    
    # MTU建议
    if [ $mtu -lt 1500 ]; then
        log_message "${YELLOW}! MTU值低于默认值1500，可能导致分片问题${NC}"
        echo -e "${YELLOW}! MTU值低于默认值1500，可能导致分片问题${NC}"
    else
        log_message "${GREEN}✓ MTU设置正常${NC}"
        echo -e "${GREEN}✓ MTU设置正常${NC}"
    fi
    
    echo -e "\n=============================="
}

# 防火墙检查
check_firewall() {
    log_message "${YELLOW}正在检查防火墙规则...${NC}"
    
    echo -e "\n====== 防火墙检查 ======\n"
    
    # 检查是否启用了防火墙
    if systemctl is-active --quiet firewalld; then
        log_message "firewalld处于活动状态"
        echo -e "firewalld处于活动状态"
        
        # 检查防火墙规则
        if firewall-cmd --list-all | grep -q "services:.*ssh"; then
            log_message "${GREEN}✓ SSH服务在防火墙中已允许${NC}"
            echo -e "${GREEN}✓ SSH服务在防火墙中已允许${NC}"
        else
            log_message "${RED}✗ SSH服务可能被防火墙阻止${NC}"
            echo -e "${RED}✗ SSH服务可能被防火墙阻止${NC}"
        fi
        
        # 检查IP地址规则
        if firewall-cmd --direct --get-all-rules | grep -q $K8S_SERVER; then
            firewall_rules=$(firewall-cmd --direct --get-all-rules | grep $K8S_SERVER)
            log_message "发现与目标服务器相关的防火墙规则: $firewall_rules"
            echo -e "发现与目标服务器相关的防火墙规则:\n$firewall_rules"
        else
            log_message "${YELLOW}! 未找到与目标服务器相关的特定防火墙规则${NC}"
            echo -e "${YELLOW}! 未找到与目标服务器相关的特定防火墙规则${NC}"
        fi
    elif command -v iptables >/dev/null 2>&1; then
        log_message "检查iptables规则"
        echo -e "检查iptables规则:"
        
        # 检查iptables规则
        iptables_rules=$(iptables-save | grep -E "${K8S_SERVER}|INPUT|FORWARD")
        log_message "iptables规则:\n$iptables_rules"
        echo -e "$iptables_rules"
        
        # 检查是否有阻止规则
        if iptables-save | grep -q "DROP.*${K8S_SERVER}"; then
            log_message "${RED}✗ 存在阻止目标服务器的iptables规则${NC}"
            echo -e "${RED}✗ 存在阻止目标服务器的iptables规则${NC}"
        else
            log_message "${GREEN}✓ 未发现阻止目标服务器的iptables规则${NC}"
            echo -e "${GREEN}✓ 未发现阻止目标服务器的iptables规则${NC}"
        fi
    else
        log_message "${YELLOW}! 未检测到活动的防火墙服务${NC}"
        echo -e "${YELLOW}! 未检测到活动的防火墙服务${NC}"
    fi
    
    echo -e "\n=============================="
}

# 云服务检查
check_cloud_services() {
    log_message "${YELLOW}正在检查云服务配置...${NC}"
    
    echo -e "\n====== 云服务配置检查 ======\n"
    
    if command -v aliyun >/dev/null 2>&1; then
        log_message "检测到阿里云CLI工具"
        echo -e "检测到阿里云CLI工具，执行云服务检查...\n"
        
        for service in "${VPC_SERVICES[@]}"; do
            echo -e "检查 $service 服务状态..."
            if aliyun $service DescribeRegions --output cols=RegionId,LocalName rows=Regions.Region[] 2>/dev/null | grep -q "RegionId"; then
                log_message "${GREEN}✓ $service 服务可访问${NC}"
                echo -e "${GREEN}✓ $service 服务可访问${NC}"
            else
                log_message "${RED}✗ $service 服务不可访问或CLI配置不正确${NC}"
                echo -e "${RED}✗ $service 服务不可访问或CLI配置不正确${NC}"
            fi
        done
    else
        log_message "${YELLOW}! 未检测到阿里云CLI工具，无法执行云服务检查${NC}"
        echo -e "${YELLOW}! 未检测到阿里云CLI工具，无法执行云服务检查${NC}"
        echo -e "建议安装阿里云CLI工具以进行更深入的检查。"
        echo -e "安装命令: pip install aliyun-cli"
    fi
    
    echo -e "\n=============================="
}

# 安全组信息收集
collect_security_group_info() {
    log_message "${YELLOW}收集安全组信息...${NC}"
    
    echo -e "\n====== 安全组信息 ======\n"
    
    if command -v aliyun >/dev/null 2>&1; then
        # 获取实例信息
        instance_id=$(curl -s http://100.100.100.200/latest/meta-data/instance-id)
        if [ -n "$instance_id" ]; then
            log_message "当前实例ID: $instance_id"
            echo -e "当前实例ID: $instance_id"
            
            # 获取安全组信息
            security_groups=$(aliyun ecs DescribeInstanceAttribute --InstanceId $instance_id --output cols=SecurityGroupIds rows=SecurityGroupIds.SecurityGroupId[] 2>/dev/null)
            log_message "安全组: $security_groups"
            echo -e "安全组:\n$security_groups"
            
            # 提取安全组ID
            sg_id=$(echo "$security_groups" | grep -v "SecurityGroupIds" | head -1)
            if [ -n "$sg_id" ]; then
                # 获取安全组规则
                echo -e "\n安全组规则:"
                aliyun ecs DescribeSecurityGroupAttribute --SecurityGroupId $sg_id --output cols=Direction,IpProtocol,PortRange,Policy rows=Permissions.Permission[] 2>/dev/null
            else
                log_message "${YELLOW}! 无法提取安全组ID${NC}"
                echo -e "${YELLOW}! 无法提取安全组ID${NC}"
            fi
        else
            log_message "${YELLOW}! 无法获取实例ID${NC}"
            echo -e "${YELLOW}! 无法获取实例ID${NC}"
        fi
    else
        log_message "${YELLOW}! 未检测到阿里云CLI工具，无法收集安全组信息${NC}"
        echo -e "${YELLOW}! 未检测到阿里云CLI工具，无法收集安全组信息${NC}"
    fi
    
    echo -e "\n=============================="
}

# VPC/VSwitch检查
check_vpc_config() {
    log_message "${YELLOW}检查VPC配置...${NC}"
    
    echo -e "\n====== VPC配置检查 ======\n"
    
    if command -v aliyun >/dev/null 2>&1; then
        # 获取VPC和VSwitch信息
        instance_id=$(curl -s http://100.100.100.200/latest/meta-data/instance-id)
        if [ -n "$instance_id" ]; then
            vpc_info=$(aliyun ecs DescribeInstanceAttribute --InstanceId $instance_id --output cols=VpcId,VSwitchId rows=[] 2>/dev/null)
            log_message "VPC信息: $vpc_info"
            echo -e "VPC信息:\n$vpc_info"
            
            # 提取VPC ID
            vpc_id=$(echo "$vpc_info" | grep "VpcId" | awk '{print $2}')
            if [ -n "$vpc_id" ]; then
                # 获取VPC路由表
                echo -e "\nVPC路由表:"
                aliyun vpc DescribeRouteTables --VpcId $vpc_id --output cols=RouteTableId,RouteEntrys.RouteEntry[].DestinationCidrBlock,RouteEntrys.RouteEntry[].NextHopType rows=RouteTables.RouteTable[] 2>/dev/null
            else
                log_message "${YELLOW}! 无法提取VPC ID${NC}"
                echo -e "${YELLOW}! 无法提取VPC ID${NC}"
            fi
        else
            log_message "${YELLOW}! 无法获取实例ID${NC}"
            echo -e "${YELLOW}! 无法获取实例ID${NC}"
        fi
    else
        log_message "${YELLOW}! 未检测到阿里云CLI工具，无法检查VPC配置${NC}"
        echo -e "${YELLOW}! 未检测到阿里云CLI工具，无法检查VPC配置${NC}"
    fi
    
    echo -e "\n=============================="
}

# 检查云企业网/高速通道
check_cloud_network() {
    log_message "${YELLOW}检查云企业网/高速通道配置...${NC}"
    
    echo -e "\n====== 云企业网/高速通道检查 ======\n"
    
    if command -v aliyun >/dev/null 2>&1; then
        # 获取VPC信息
        instance_id=$(curl -s http://100.100.100.200/latest/meta-data/instance-id)
        if [ -n "$instance_id" ]; then
            vpc_id=$(aliyun ecs DescribeInstanceAttribute --InstanceId $instance_id --output cols=VpcId rows=[] 2>/dev/null | grep "VpcId" | awk '{print $2}')
            if [ -n "$vpc_id" ]; then
                # 检查是否加入了云企业网
                cen_info=$(aliyun cen DescribeCenAttachedChildInstances --output cols=CenId,ChildInstanceId rows=ChildInstances.ChildInstance[] 2>/dev/null | grep $vpc_id)
                if [ -n "$cen_info" ]; then
                    log_message "${GREEN}✓ 当前VPC已加入云企业网${NC}"
                    echo -e "${GREEN}✓ 当前VPC已加入云企业网${NC}"
                    echo -e "$cen_info"
                    
                    # 提取云企业网ID
                    cen_id=$(echo "$cen_info" | awk '{print $1}')
                    if [ -n "$cen_id" ]; then
                        # 获取云企业网路由
                        echo -e "\n云企业网路由:"
                        aliyun cen DescribeCenRouteTables --CenId $cen_id --output cols=DestinationCidrBlock,Type,NextHopInstanceId rows=CenRouteTables.CenRouteTable[].CenRouteEntries.CenRouteEntry[] 2>/dev/null
                    fi
                else
                    log_message "${YELLOW}! 当前VPC未加入云企业网${NC}"
                    echo -e "${YELLOW}! 当前VPC未加入云企业网${NC}"
                    
                    # 检查高速通道
                    express_route=$(aliyun vpc DescribeVpcAttribute --VpcId $vpc_id --output cols=VpcId,RouterTableIds rows=[] 2>/dev/null)
                    if [ -n "$express_route" ]; then
                        echo -e "\n检查高速通道配置..."
                        # 这里需要根据实际API调整
                        # 阿里云高速通道API较为复杂，这里只是一个示例
                        echo -e "${YELLOW}! 需要进一步检查高速通道配置${NC}"
                    fi
                fi
            else
                log_message "${YELLOW}! 无法提取VPC ID${NC}"
                echo -e "${YELLOW}! 无法提取VPC ID${NC}"
            fi
        else
            log_message "${YELLOW}! 无法获取实例ID${NC}"
            echo -e "${YELLOW}! 无法获取实例ID${NC}"
        fi
    else
        log_message "${YELLOW}! 未检测到阿里云CLI工具，无法检查云企业网/高速通道配置${NC}"
        echo -e "${YELLOW}! 未检测到阿里云CLI工具，无法检查云企业网/高速通道配置${NC}"
    fi
    
    echo -e "\n=============================="
}

# 生成诊断报告
generate_report() {
    report_file="vpc_diagnostic_report_$(date +%Y%m%d_%H%M%S).txt"
    log_message "${YELLOW}生成诊断报告: $report_file${NC}"
    
    echo -e "\n====== 生成诊断报告 ======\n"
    echo -e "报告文件: $report_file"
    
    # 复制日志内容到报告文件
    cat $LOG_FILE > $report_file
    
    # 添加系统信息
    echo -e "\n\n====== 系统信息 ======" >> $report_file
    echo -e "操作系统:" >> $report_file
    cat /etc/os-release >> $report_file
    echo -e "\n内核版本:" >> $report_file
    uname -a >> $report_file
    
    # 添加网络接口信息
    echo -e "\n\n====== 网络接口信息 ======" >> $report_file
    ip addr >> $report_file
    
    # 添加路由表
    echo -e "\n\n====== 路由表 ======" >> $report_file
    ip route >> $report_file
    
    # 添加防火墙信息
    echo -e "\n\n====== 防火墙信息 ======" >> $report_file
    if command -v iptables >/dev/null 2>&1; then
        iptables-save >> $report_file 2>/dev/null
    fi
    
    # 添加诊断结论和建议
    echo -e "\n\n====== 诊断结论和建议 ======" >> $report_file
    
    # 根据检查结果生成结论
    if ping -c 1 -W 2 $K8S_SERVER > /dev/null 2>&1; then
        echo -e "- ICMP连接正常，基本网络连通性良好" >> $report_file
    else
        echo -e "- ICMP连接失败，可能存在以下问题:" >> $report_file
        echo -e "  * 防火墙阻止了ICMP流量" >> $report_file
        echo -e "  * 两个VPC之间未正确配置路由" >> $report_file
        echo -e "  * 安全组规则阻止了ICMP流量" >> $report_file
        echo -e "  * 云企业网/高速通道配置不正确" >> $report_file
    fi
    
    if nc -z -w $TIMEOUT $K8S_SERVER $SSH_PORT > /dev/null 2>&1; then
        echo -e "- SSH端口连接正常" >> $report_file
    else
        echo -e "- SSH端口连接失败，可能存在以下问题:" >> $report_file
        echo -e "  * 目标服务器上的SSH服务未运行" >> $report_file
        echo -e "  * 防火墙阻止了SSH流量" >> $report_file
        echo -e "  * 安全组规则阻止了SSH流量" >> $report_file
    fi
    
    if nc -z -w $TIMEOUT $K8S_SERVER $HTTP_PORT > /dev/null 2>&1; then
        echo -e "- HTTP端口连接正常" >> $report_file
    else
        echo -e "- HTTP端口连接失败，可能存在以下问题:" >> $report_file
        echo -e "  * 目标服务器上的HTTP服务未运行" >> $report_file
        echo -e "  * 防火墙阻止了HTTP流量" >> $report_file
        echo -e "  * 安全组规则阻止了HTTP流量" >> $report_file
    fi
    
    # 添加推荐解决方案
    echo -e "\n推荐解决方案:" >> $report_file
    echo -e "1. 检查两个VPC的安全组规则，确保允许必要的流量" >> $report_file
    echo -e "2. 确保已经配置了云企业网或高速通道，使两个VPC可以通信" >> $report_file
    echo -e "3. 检查VPC路由表，确保路由条目正确" >> $report_file
    echo -e "4. 如果使用了自定义防火墙规则，请检查是否阻止了必要的流量" >> $report_file
    echo -e "5. 如果以上步骤未解决问题，请考虑使用VPC对等连接或VPN隧道" >> $report_file
    
    log_message "${GREEN}诊断报告已生成: $report_file${NC}"
    echo -e "${GREEN}诊断报告已生成: $report_file${NC}\n"
}

# 显示帮助信息
show_help() {
    echo "VPC直连诊断工具"
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help         显示此帮助信息"
    echo "  -b, --basic        运行基本连接检查"
    echo "  -r, --routing      检查路由配置"
    echo "  -f, --firewall     检查防火墙规则"
    echo "  -c, --cloud        检查云服务配置"
    echo "  -a, --all          运行所有检查 (默认)"
    echo "  -o, --report       生成诊断报告"
    echo ""
}

# 主函数
main() {
    # 解析命令行参数
    if [ $# -eq 0 ]; then
        run_all=true
    else
        case "$1" in
            -h|--help)
                show_help
                exit 0
                ;;
            -b|--basic)
                check_basic=true
                ;;
            -r|--routing)
                check_route=true
                ;;
            -f|--firewall)
                check_fw=true
                ;;
            -c|--cloud)
                check_cloud=true
                ;;
            -a|--all)
                run_all=true
                ;;
            -o|--report)
                gen_report=true
                ;;
            *)
                show_help
                exit 1
                ;;
        esac
    fi
    
    # 显示工具标题
    show_header
    
    # 根据选项运行相应的检查
    if [ "$run_all" = true ] || [ "$check_basic" = true ]; then
        check_basic_connectivity
    fi
    
    if [ "$run_all" = true ] || [ "$check_route" = true ]; then
        check_routing
        check_mtu
    fi
    
    if [ "$run_all" = true ] || [ "$check_fw" = true ]; then
        check_firewall
    fi
    
    if [ "$run_all" = true ] || [ "$check_cloud" = true ]; then
        check_cloud_services
        collect_security_group_info
        check_vpc_config
        check_cloud_network
    fi
    
    if [ "$run_all" = true ] || [ "$gen_report" = true ]; then
        generate_report
    fi
    
    # 显示完成信息
    echo -e "\n${GREEN}诊断完成！${NC}"
    echo -e "详细日志已保存到: $LOG_FILE"
}

# 执行主函数
main "$@" 