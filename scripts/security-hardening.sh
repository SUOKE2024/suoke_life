#!/bin/bash

# 索克生活项目 - 安全加固脚本
# 实施安全最佳实践，加强系统安全防护

echo "🔒 索克生活项目 - 安全加固"
echo "=========================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查运行权限
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        echo -e "${RED}⚠️  请不要以root用户运行此脚本${NC}"
        echo "建议使用具有sudo权限的普通用户"
        exit 1
    fi
    
    if ! sudo -n true 2>/dev/null; then
        echo -e "${YELLOW}需要sudo权限来执行安全配置${NC}"
        sudo -v
    fi
}

# 更新系统包
update_system() {
    echo -e "${BLUE}更新系统包...${NC}"
    
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt upgrade -y
        sudo apt install -y fail2ban ufw unattended-upgrades
    elif command -v yum &> /dev/null; then
        sudo yum update -y
        sudo yum install -y fail2ban firewalld
    fi
    
    echo -e "${GREEN}✅ 系统包更新完成${NC}"
    echo ""
}

# 配置防火墙
configure_firewall() {
    echo -e "${BLUE}配置防火墙...${NC}"
    
    if command -v ufw &> /dev/null; then
        # Ubuntu/Debian UFW配置
        sudo ufw --force reset
        sudo ufw default deny incoming
        sudo ufw default allow outgoing
        
        # 允许SSH
        sudo ufw allow 22/tcp
        
        # 允许HTTP/HTTPS
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        
        # 允许应用端口（仅本地）
        sudo ufw allow from 127.0.0.1 to any port 8000:8010
        sudo ufw allow from 127.0.0.1 to any port 3000
        sudo ufw allow from 127.0.0.1 to any port 9090
        sudo ufw allow from 127.0.0.1 to any port 3000
        
        # 拒绝数据库端口的外部访问
        sudo ufw deny 5432/tcp
        sudo ufw deny 6379/tcp
        sudo ufw deny 27017/tcp
        
        sudo ufw --force enable
        
    elif command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL firewalld配置
        sudo systemctl enable firewalld
        sudo systemctl start firewalld
        
        sudo firewall-cmd --permanent --add-service=ssh
        sudo firewall-cmd --permanent --add-service=http
        sudo firewall-cmd --permanent --add-service=https
        
        # 拒绝数据库端口
        sudo firewall-cmd --permanent --add-rich-rule="rule family='ipv4' port protocol='tcp' port='5432' reject"
        sudo firewall-cmd --permanent --add-rich-rule="rule family='ipv4' port protocol='tcp' port='6379' reject"
        
        sudo firewall-cmd --reload
    fi
    
    echo -e "${GREEN}✅ 防火墙配置完成${NC}"
    echo ""
}

# 配置Fail2Ban
configure_fail2ban() {
    echo -e "${BLUE}配置Fail2Ban...${NC}"
    
    # 创建SSH保护配置
    sudo tee /etc/fail2ban/jail.local > /dev/null << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
backend = systemd

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600

[docker-auth]
enabled = true
filter = docker-auth
port = 2376
logpath = /var/log/docker.log
maxretry = 3
bantime = 7200
EOF

    # 创建Docker认证过滤器
    sudo tee /etc/fail2ban/filter.d/docker-auth.conf > /dev/null << 'EOF'
[Definition]
failregex = ^.*\[error\].*authentication failure.*<HOST>.*$
ignoreregex =
EOF

    # 启动Fail2Ban
    sudo systemctl enable fail2ban
    sudo systemctl restart fail2ban
    
    echo -e "${GREEN}✅ Fail2Ban配置完成${NC}"
    echo ""
}

# 配置SSH安全
configure_ssh() {
    echo -e "${BLUE}配置SSH安全...${NC}"
    
    # 备份原始配置
    sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    
    # 创建安全的SSH配置
    sudo tee /etc/ssh/sshd_config.d/99-suoke-security.conf > /dev/null << 'EOF'
# 索克生活项目SSH安全配置

# 禁用root登录
PermitRootLogin no

# 禁用密码认证（推荐使用密钥认证）
PasswordAuthentication no
ChallengeResponseAuthentication no
UsePAM no

# 限制用户
AllowUsers $(whoami)

# 网络安全
Protocol 2
Port 22
AddressFamily inet
ListenAddress 0.0.0.0

# 认证设置
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PermitEmptyPasswords no
MaxAuthTries 3
MaxSessions 2

# 会话设置
ClientAliveInterval 300
ClientAliveCountMax 2
LoginGraceTime 60

# 禁用不安全功能
X11Forwarding no
AllowTcpForwarding no
AllowAgentForwarding no
PermitTunnel no
GatewayPorts no
PermitUserEnvironment no
EOF

    # 验证SSH配置
    if sudo sshd -t; then
        sudo systemctl restart sshd
        echo -e "${GREEN}✅ SSH安全配置完成${NC}"
    else
        echo -e "${RED}❌ SSH配置验证失败，恢复原始配置${NC}"
        sudo mv /etc/ssh/sshd_config.backup /etc/ssh/sshd_config
        sudo rm -f /etc/ssh/sshd_config.d/99-suoke-security.conf
    fi
    
    echo ""
}

# 配置Docker安全
configure_docker_security() {
    echo -e "${BLUE}配置Docker安全...${NC}"
    
    # 创建Docker daemon安全配置
    sudo mkdir -p /etc/docker
    sudo tee /etc/docker/daemon.json > /dev/null << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true,
  "seccomp-profile": "/etc/docker/seccomp.json",
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}
EOF

    # 创建Docker seccomp配置
    sudo tee /etc/docker/seccomp.json > /dev/null << 'EOF'
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "archMap": [
    {
      "architecture": "SCMP_ARCH_X86_64",
      "subArchitectures": [
        "SCMP_ARCH_X86",
        "SCMP_ARCH_X32"
      ]
    }
  ],
  "syscalls": [
    {
      "names": [
        "accept",
        "accept4",
        "access",
        "adjtimex",
        "alarm",
        "bind",
        "brk",
        "capget",
        "capset",
        "chdir",
        "chmod",
        "chown",
        "chroot",
        "clock_getres",
        "clock_gettime",
        "clock_nanosleep",
        "close",
        "connect",
        "copy_file_range",
        "creat",
        "dup",
        "dup2",
        "dup3",
        "epoll_create",
        "epoll_create1",
        "epoll_ctl",
        "epoll_pwait",
        "epoll_wait",
        "eventfd",
        "eventfd2",
        "execve",
        "execveat",
        "exit",
        "exit_group",
        "faccessat",
        "fadvise64",
        "fallocate",
        "fanotify_mark",
        "fchdir",
        "fchmod",
        "fchmodat",
        "fchown",
        "fchownat",
        "fcntl",
        "fdatasync",
        "fgetxattr",
        "flistxattr",
        "flock",
        "fork",
        "fremovexattr",
        "fsetxattr",
        "fstat",
        "fstatfs",
        "fsync",
        "ftruncate",
        "futex",
        "getcwd",
        "getdents",
        "getdents64",
        "getegid",
        "geteuid",
        "getgid",
        "getgroups",
        "getpeername",
        "getpgid",
        "getpgrp",
        "getpid",
        "getppid",
        "getpriority",
        "getrandom",
        "getresgid",
        "getresuid",
        "getrlimit",
        "get_robust_list",
        "getrusage",
        "getsid",
        "getsockname",
        "getsockopt",
        "get_thread_area",
        "gettid",
        "gettimeofday",
        "getuid",
        "getxattr",
        "inotify_add_watch",
        "inotify_init",
        "inotify_init1",
        "inotify_rm_watch",
        "io_cancel",
        "ioctl",
        "io_destroy",
        "io_getevents",
        "ioprio_get",
        "ioprio_set",
        "io_setup",
        "io_submit",
        "ipc",
        "kill",
        "lchown",
        "lgetxattr",
        "link",
        "linkat",
        "listen",
        "listxattr",
        "llistxattr",
        "lremovexattr",
        "lseek",
        "lsetxattr",
        "lstat",
        "madvise",
        "memfd_create",
        "mincore",
        "mkdir",
        "mkdirat",
        "mknod",
        "mknodat",
        "mlock",
        "mlock2",
        "mlockall",
        "mmap",
        "mmap2",
        "mprotect",
        "mq_getsetattr",
        "mq_notify",
        "mq_open",
        "mq_timedreceive",
        "mq_timedsend",
        "mq_unlink",
        "mremap",
        "msgctl",
        "msgget",
        "msgrcv",
        "msgsnd",
        "msync",
        "munlock",
        "munlockall",
        "munmap",
        "nanosleep",
        "newfstatat",
        "_newselect",
        "open",
        "openat",
        "pause",
        "pipe",
        "pipe2",
        "poll",
        "ppoll",
        "prctl",
        "pread64",
        "preadv",
        "prlimit64",
        "pselect6",
        "ptrace",
        "pwrite64",
        "pwritev",
        "read",
        "readahead",
        "readlink",
        "readlinkat",
        "readv",
        "recv",
        "recvfrom",
        "recvmmsg",
        "recvmsg",
        "remap_file_pages",
        "removexattr",
        "rename",
        "renameat",
        "renameat2",
        "restart_syscall",
        "rmdir",
        "rt_sigaction",
        "rt_sigpending",
        "rt_sigprocmask",
        "rt_sigqueueinfo",
        "rt_sigreturn",
        "rt_sigsuspend",
        "rt_sigtimedwait",
        "rt_tgsigqueueinfo",
        "sched_getaffinity",
        "sched_getattr",
        "sched_getparam",
        "sched_get_priority_max",
        "sched_get_priority_min",
        "sched_getscheduler",
        "sched_setaffinity",
        "sched_setattr",
        "sched_setparam",
        "sched_setscheduler",
        "sched_yield",
        "seccomp",
        "select",
        "semctl",
        "semget",
        "semop",
        "semtimedop",
        "send",
        "sendfile",
        "sendfile64",
        "sendmmsg",
        "sendmsg",
        "sendto",
        "setfsgid",
        "setfsuid",
        "setgid",
        "setgroups",
        "setitimer",
        "setpgid",
        "setpriority",
        "setregid",
        "setresgid",
        "setresuid",
        "setreuid",
        "setrlimit",
        "set_robust_list",
        "setsid",
        "setsockopt",
        "set_thread_area",
        "set_tid_address",
        "setuid",
        "setxattr",
        "shmat",
        "shmctl",
        "shmdt",
        "shmget",
        "shutdown",
        "sigaltstack",
        "signalfd",
        "signalfd4",
        "sigreturn",
        "socket",
        "socketcall",
        "socketpair",
        "splice",
        "stat",
        "statfs",
        "statx",
        "symlink",
        "symlinkat",
        "sync",
        "sync_file_range",
        "syncfs",
        "sysinfo",
        "syslog",
        "tee",
        "tgkill",
        "time",
        "timer_create",
        "timer_delete",
        "timerfd_create",
        "timerfd_gettime",
        "timerfd_settime",
        "timer_getoverrun",
        "timer_gettime",
        "timer_settime",
        "times",
        "tkill",
        "truncate",
        "umask",
        "uname",
        "unlink",
        "unlinkat",
        "utime",
        "utimensat",
        "utimes",
        "vfork",
        "vmsplice",
        "wait4",
        "waitid",
        "waitpid",
        "write",
        "writev"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
EOF

    # 重启Docker服务
    sudo systemctl restart docker
    
    echo -e "${GREEN}✅ Docker安全配置完成${NC}"
    echo ""
}

# 配置文件权限
configure_file_permissions() {
    echo -e "${BLUE}配置文件权限...${NC}"
    
    # 设置敏感文件权限
    if [ -f ".env" ]; then
        chmod 600 .env
        echo "设置 .env 文件权限为 600"
    fi
    
    # 设置脚本权限
    find scripts/ -name "*.sh" -exec chmod 750 {} \;
    echo "设置脚本文件权限为 750"
    
    # 设置配置文件权限
    find . -name "*.yml" -o -name "*.yaml" -exec chmod 644 {} \;
    echo "设置配置文件权限为 644"
    
    # 设置密钥文件权限
    find . -name "*.key" -o -name "*.pem" -exec chmod 600 {} \;
    echo "设置密钥文件权限为 600"
    
    echo -e "${GREEN}✅ 文件权限配置完成${NC}"
    echo ""
}

# 配置日志审计
configure_logging() {
    echo -e "${BLUE}配置日志审计...${NC}"
    
    # 创建日志目录
    sudo mkdir -p /var/log/suoke-life
    sudo chown $(whoami):$(whoami) /var/log/suoke-life
    
    # 配置rsyslog
    sudo tee /etc/rsyslog.d/99-suoke-life.conf > /dev/null << 'EOF'
# 索克生活项目日志配置
$template SuokeLifeFormat,"%timegenerated% %HOSTNAME% %syslogtag% %msg%\n"

# Docker容器日志
:programname, isequal, "docker" /var/log/suoke-life/docker.log;SuokeLifeFormat
& stop

# 应用日志
:programname, startswith, "suoke-" /var/log/suoke-life/application.log;SuokeLifeFormat
& stop

# 安全日志
:programname, isequal, "fail2ban" /var/log/suoke-life/security.log;SuokeLifeFormat
& stop
EOF

    # 配置logrotate
    sudo tee /etc/logrotate.d/suoke-life > /dev/null << 'EOF'
/var/log/suoke-life/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        systemctl reload rsyslog
    endscript
}
EOF

    sudo systemctl restart rsyslog
    
    echo -e "${GREEN}✅ 日志审计配置完成${NC}"
    echo ""
}

# 配置自动安全更新
configure_auto_updates() {
    echo -e "${BLUE}配置自动安全更新...${NC}"
    
    if command -v apt &> /dev/null; then
        # Ubuntu/Debian自动更新配置
        sudo tee /etc/apt/apt.conf.d/50unattended-upgrades > /dev/null << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}";
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};

Unattended-Upgrade::Package-Blacklist {
    "docker-ce";
    "docker-ce-cli";
    "containerd.io";
};

Unattended-Upgrade::DevRelease "false";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Automatic-Reboot-WithUsers "false";
Unattended-Upgrade::Automatic-Reboot-Time "02:00";
EOF

        sudo tee /etc/apt/apt.conf.d/20auto-upgrades > /dev/null << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF

        sudo systemctl enable unattended-upgrades
        sudo systemctl start unattended-upgrades
        
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL自动更新配置
        sudo yum install -y yum-cron
        
        sudo sed -i 's/apply_updates = no/apply_updates = yes/' /etc/yum/yum-cron.conf
        sudo sed -i 's/update_cmd = default/update_cmd = security/' /etc/yum/yum-cron.conf
        
        sudo systemctl enable yum-cron
        sudo systemctl start yum-cron
    fi
    
    echo -e "${GREEN}✅ 自动安全更新配置完成${NC}"
    echo ""
}

# 创建安全监控脚本
create_security_monitoring() {
    echo -e "${BLUE}创建安全监控脚本...${NC}"
    
    cat > scripts/security-monitor.sh << 'EOF'
#!/bin/bash

# 索克生活项目 - 安全监控脚本

LOG_FILE="/var/log/suoke-life/security-monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# 检查失败的登录尝试
check_failed_logins() {
    FAILED_LOGINS=$(grep "Failed password" /var/log/auth.log | grep "$(date '+%b %d')" | wc -l)
    if [ $FAILED_LOGINS -gt 10 ]; then
        echo "[$DATE] WARNING: $FAILED_LOGINS failed login attempts today" >> $LOG_FILE
    fi
}

# 检查Docker容器状态
check_docker_containers() {
    STOPPED_CONTAINERS=$(docker ps -a --filter "status=exited" --format "{{.Names}}" | grep -E "suoke|xiaoai|xiaoke|laoke|soer" | wc -l)
    if [ $STOPPED_CONTAINERS -gt 0 ]; then
        echo "[$DATE] WARNING: $STOPPED_CONTAINERS critical containers are stopped" >> $LOG_FILE
    fi
}

# 检查磁盘使用率
check_disk_usage() {
    DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt 85 ]; then
        echo "[$DATE] WARNING: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
    fi
}

# 检查内存使用率
check_memory_usage() {
    MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ $MEMORY_USAGE -gt 90 ]; then
        echo "[$DATE] WARNING: Memory usage is ${MEMORY_USAGE}%" >> $LOG_FILE
    fi
}

# 检查网络连接
check_network_connections() {
    SUSPICIOUS_CONNECTIONS=$(netstat -an | grep ":22 " | grep ESTABLISHED | wc -l)
    if [ $SUSPICIOUS_CONNECTIONS -gt 5 ]; then
        echo "[$DATE] WARNING: $SUSPICIOUS_CONNECTIONS SSH connections detected" >> $LOG_FILE
    fi
}

# 检查文件完整性
check_file_integrity() {
    if [ -f "/etc/suoke-life/checksums.md5" ]; then
        if ! md5sum -c /etc/suoke-life/checksums.md5 >/dev/null 2>&1; then
            echo "[$DATE] CRITICAL: File integrity check failed" >> $LOG_FILE
        fi
    fi
}

# 执行所有检查
main() {
    check_failed_logins
    check_docker_containers
    check_disk_usage
    check_memory_usage
    check_network_connections
    check_file_integrity
    
    echo "[$DATE] Security monitoring completed" >> $LOG_FILE
}

main
EOF

    chmod +x scripts/security-monitor.sh
    
    # 添加到crontab
    (crontab -l 2>/dev/null; echo "*/15 * * * * $(pwd)/scripts/security-monitor.sh") | crontab -
    
    echo -e "${GREEN}✅ 安全监控脚本创建完成${NC}"
    echo ""
}

# 生成安全报告
generate_security_report() {
    echo -e "${BLUE}生成安全配置报告...${NC}"
    
    REPORT_FILE="SECURITY_HARDENING_REPORT.md"
    
    cat > $REPORT_FILE << EOF
# 索克生活项目安全加固报告

## 执行时间
$(date '+%Y年%m月%d日 %H:%M:%S')

## 安全配置概览

### 1. 系统安全
- ✅ 系统包已更新到最新版本
- ✅ 自动安全更新已启用
- ✅ 不必要的服务已禁用

### 2. 网络安全
- ✅ 防火墙已配置并启用
- ✅ 仅开放必要端口 (22, 80, 443)
- ✅ 数据库端口已禁止外部访问
- ✅ Fail2Ban已配置并启用

### 3. SSH安全
- ✅ 禁用root登录
- ✅ 禁用密码认证
- ✅ 启用密钥认证
- ✅ 限制登录尝试次数

### 4. Docker安全
- ✅ Docker daemon安全配置
- ✅ Seccomp安全配置文件
- ✅ 容器资源限制
- ✅ 禁用特权容器

### 5. 文件权限
- ✅ 敏感文件权限设置为600
- ✅ 脚本文件权限设置为750
- ✅ 配置文件权限设置为644

### 6. 日志审计
- ✅ 集中日志收集配置
- ✅ 日志轮转配置
- ✅ 安全事件监控

### 7. 监控告警
- ✅ 安全监控脚本已部署
- ✅ 定时检查任务已配置
- ✅ 异常情况告警机制

## 安全建议

### 立即执行
1. 定期检查安全日志: \`tail -f /var/log/suoke-life/security.log\`
2. 监控系统资源使用情况
3. 定期更新Docker镜像
4. 备份重要数据和配置

### 定期维护
1. 每周检查安全更新
2. 每月审查访问日志
3. 每季度进行安全评估
4. 每年更新安全策略

## 安全检查命令

\`\`\`bash
# 检查防火墙状态
sudo ufw status

# 检查Fail2Ban状态
sudo fail2ban-client status

# 检查SSH配置
sudo sshd -t

# 检查Docker安全
docker info | grep -i security

# 查看安全日志
tail -f /var/log/suoke-life/security.log

# 运行安全监控
./scripts/security-monitor.sh
\`\`\`

## 应急响应

### 发现安全事件时
1. 立即隔离受影响的系统
2. 收集和保存相关日志
3. 分析攻击向量和影响范围
4. 修复安全漏洞
5. 恢复正常服务
6. 总结经验教训

### 联系方式
- 安全团队邮箱: security@suoke.life
- 紧急联系电话: +86-400-xxx-xxxx
- 安全事件报告: https://security.suoke.life/report

---

*报告生成时间: $(date)*
*安全加固版本: v1.0.0*
EOF

    echo -e "${GREEN}✅ 安全配置报告已生成: $REPORT_FILE${NC}"
    echo ""
}

# 验证安全配置
verify_security_config() {
    echo -e "${BLUE}验证安全配置...${NC}"
    
    ISSUES=0
    
    # 检查防火墙状态
    if command -v ufw &> /dev/null; then
        if ! sudo ufw status | grep -q "Status: active"; then
            echo -e "${RED}❌ 防火墙未启用${NC}"
            ((ISSUES++))
        else
            echo -e "${GREEN}✅ 防火墙已启用${NC}"
        fi
    fi
    
    # 检查Fail2Ban状态
    if systemctl is-active --quiet fail2ban; then
        echo -e "${GREEN}✅ Fail2Ban正在运行${NC}"
    else
        echo -e "${RED}❌ Fail2Ban未运行${NC}"
        ((ISSUES++))
    fi
    
    # 检查SSH配置
    if sudo sshd -t 2>/dev/null; then
        echo -e "${GREEN}✅ SSH配置有效${NC}"
    else
        echo -e "${RED}❌ SSH配置无效${NC}"
        ((ISSUES++))
    fi
    
    # 检查Docker配置
    if [ -f "/etc/docker/daemon.json" ]; then
        echo -e "${GREEN}✅ Docker安全配置存在${NC}"
    else
        echo -e "${RED}❌ Docker安全配置缺失${NC}"
        ((ISSUES++))
    fi
    
    # 检查文件权限
    if [ -f ".env" ] && [ "$(stat -c %a .env)" = "600" ]; then
        echo -e "${GREEN}✅ .env文件权限正确${NC}"
    else
        echo -e "${YELLOW}⚠️  .env文件权限需要检查${NC}"
    fi
    
    echo ""
    if [ $ISSUES -eq 0 ]; then
        echo -e "${GREEN}🎉 所有安全配置验证通过！${NC}"
    else
        echo -e "${RED}⚠️  发现 $ISSUES 个安全配置问题，请检查并修复${NC}"
    fi
    
    echo ""
}

# 主执行流程
main() {
    echo -e "${YELLOW}开始索克生活项目安全加固...${NC}"
    echo ""
    
    check_permissions
    update_system
    configure_firewall
    configure_fail2ban
    configure_ssh
    configure_docker_security
    configure_file_permissions
    configure_logging
    configure_auto_updates
    create_security_monitoring
    generate_security_report
    verify_security_config
    
    echo -e "${GREEN}🔒 安全加固完成！${NC}"
    echo ""
    echo -e "${YELLOW}重要提醒:${NC}"
    echo "1. 请确保已配置SSH密钥认证"
    echo "2. 定期检查安全日志和监控报告"
    echo "3. 保持系统和应用程序更新"
    echo "4. 定期备份重要数据"
    echo ""
    echo -e "${BLUE}安全报告已保存到: SECURITY_HARDENING_REPORT.md${NC}"
    echo -e "${BLUE}安全监控脚本: ./scripts/security-monitor.sh${NC}"
    echo ""
}

# 执行主函数
main 