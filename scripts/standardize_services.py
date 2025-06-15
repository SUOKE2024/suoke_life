#!/usr/bin/env python3
"""
索克生活微服务标准化脚本

用于批量更新微服务的配置文件，确保一致性。
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import yaml
import json

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SERVICES_DIR = PROJECT_ROOT / "services"

# 标准化配置
STANDARD_CONFIG = {
    "python_version": "3.13.3",
    "rest_port": 8080,
    "grpc_port": 50051,
    "health_endpoint": "/health",
    "api_prefix": "/api/v1",
    "docker_user": "suoke",
    "docker_group": "suoke"
}

# 需要标准化的服务列表
SERVICES_TO_STANDARDIZE = [
    "auth-service",
    "user-service", 
    "agent-services/soer-service",
    "agent-services/xiaoke-service",
    "agent-services/laoke-service",
    "agent-services/xiaoai-service",
    "diagnostic-services/look-service",
    "diagnostic-services/listen-service",
    "diagnostic-services/palpation-service",
    "diagnostic-services/calculation-service",
    "diagnostic-services/inquiry-service",
    "rag-service",
    "api-gateway",
    "blockchain-service",
    "human-review-service",
    "accessibility-service",
    "med-knowledge",
    "health-data-service",
    "suoke-bench-service"
]

def log_info(message: str):
    """打印信息日志"""
    print(f"[INFO] {message}")

def log_warning(message: str):
    """打印警告日志"""
    print(f"[WARNING] {message}")

def log_error(message: str):
    """打印错误日志"""
    print(f"[ERROR] {message}")

def create_standard_dockerfile(service_path: Path, service_name: str) -> str:
    """创建标准化的Dockerfile"""
    dockerfile_content = f'''# 标准化的多阶段构建Dockerfile - 使用UV包管理器
# 构建阶段
FROM python:{STANDARD_CONFIG["python_version"]}-slim AS builder

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PIP_NO_CACHE_DIR=1 \\
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    gcc \\
    g++ \\
    libpq-dev \\
    libffi-dev \\
    libssl-dev \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# 安装UV包管理器
RUN pip install uv

# 设置工作目录
WORKDIR /app

# 复制项目配置文件
COPY pyproject.toml uv.lock* ./

# 创建虚拟环境并安装依赖
RUN uv venv && \\
    uv pip install -e .

# 运行阶段
FROM python:{STANDARD_CONFIG["python_version"]}-slim AS runtime

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PATH="/app/.venv/bin:$PATH" \\
    PYTHONPATH="/app"

# 创建非root用户
RUN groupadd -r {STANDARD_CONFIG["docker_group"]} && useradd -r -g {STANDARD_CONFIG["docker_group"]} -d /app -s /bin/bash {STANDARD_CONFIG["docker_user"]}

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \\
    libpq5 \\
    libgomp1 \\
    curl \\
    ca-certificates \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

# 设置工作目录
WORKDIR /app

# 从构建阶段复制虚拟环境
COPY --from=builder /app/.venv /app/.venv

# 复制应用代码
COPY --chown={STANDARD_CONFIG["docker_user"]}:{STANDARD_CONFIG["docker_group"]} . .

# 创建必要的目录
RUN mkdir -p /app/logs /app/data /app/cache && \\
    chown -R {STANDARD_CONFIG["docker_user"]}:{STANDARD_CONFIG["docker_group"]} /app

# 切换到非root用户
USER {STANDARD_CONFIG["docker_user"]}

# 暴露端口 (统一端口规范)
EXPOSE {STANDARD_CONFIG["rest_port"]} {STANDARD_CONFIG["grpc_port"]}

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{STANDARD_CONFIG["rest_port"]}{STANDARD_CONFIG["health_endpoint"]} || exit 1

# 启动命令
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{STANDARD_CONFIG["rest_port"]}"]
'''
    return dockerfile_content

def create_standard_docker_compose(service_name: str) -> str:
    """创建标准化的docker-compose.yml"""
    compose_content = f'''# 索克生活{service_name}服务 Docker Compose 配置
version: '3.8'

services:
  {service_name}:
    build:
      context: .
      dockerfile: Dockerfile
      target: runtime
    container_name: suoke-{service_name}
    restart: unless-stopped
    ports:
      - "{STANDARD_CONFIG["rest_port"]}:{STANDARD_CONFIG["rest_port"]}"  # REST API
      - "{STANDARD_CONFIG["grpc_port"]}:{STANDARD_CONFIG["grpc_port"]}"  # gRPC
    environment:
      # 服务配置
      - SERVICE_NAME={service_name}
      - SERVICE_VERSION=2.0.0
      - SERVICE_ENV=production
      - REST_PORT={STANDARD_CONFIG["rest_port"]}
      - GRPC_PORT={STANDARD_CONFIG["grpc_port"]}
      
      # 数据库配置
      - DATABASE_URL=postgresql://user:password@postgres:5432/{service_name.replace("-", "_")}db
      - REDIS_URL=redis://redis:6379/0
      
      # 监控配置
      - ENABLE_METRICS=true
      - ENABLE_TRACING=true
      - JAEGER_ENDPOINT=http://jaeger:14268/api/traces
      
      # 日志配置
      - LOG_LEVEL=INFO
      - LOG_FORMAT=json
    volumes:
      - {service_name}_data:/app/data
      - ./logs:/app/logs
    networks:
      - suoke-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{STANDARD_CONFIG["rest_port"]}{STANDARD_CONFIG["health_endpoint"]}"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  {service_name}_data:
    driver: local

networks:
  suoke-network:
    external: true
'''
    return compose_content

def update_service_dockerfile(service_path: Path, service_name: str):
    """更新服务的Dockerfile"""
    dockerfile_path = service_path / "Dockerfile"
    
    # 备份原文件
    if dockerfile_path.exists():
        backup_path = dockerfile_path.with_suffix(".dockerfile.backup")
        shutil.copy2(dockerfile_path, backup_path)
        log_info(f"备份原Dockerfile到 {backup_path}")
    
    # 创建新的标准化Dockerfile
    dockerfile_content = create_standard_dockerfile(service_path, service_name)
    
    with open(dockerfile_path, 'w', encoding='utf-8') as f:
        f.write(dockerfile_content)
    
    log_info(f"更新 {service_name} 的Dockerfile")

def update_service_compose(service_path: Path, service_name: str):
    """更新服务的docker-compose.yml"""
    compose_path = service_path / "docker-compose.yml"
    
    # 备份原文件
    if compose_path.exists():
        backup_path = compose_path.with_suffix(".yml.backup")
        shutil.copy2(compose_path, backup_path)
        log_info(f"备份原docker-compose.yml到 {backup_path}")
    
    # 创建新的标准化docker-compose.yml
    compose_content = create_standard_docker_compose(service_name)
    
    with open(compose_path, 'w', encoding='utf-8') as f:
        f.write(compose_content)
    
    log_info(f"更新 {service_name} 的docker-compose.yml")

def remove_requirements_txt(service_path: Path, service_name: str):
    """移除requirements.txt文件（如果存在pyproject.toml）"""
    requirements_path = service_path / "requirements.txt"
    pyproject_path = service_path / "pyproject.toml"
    
    if requirements_path.exists() and pyproject_path.exists():
        backup_path = requirements_path.with_suffix(".txt.backup")
        shutil.move(requirements_path, backup_path)
        log_info(f"移除 {service_name} 的requirements.txt（已备份到 {backup_path}）")

def create_uv_lock(service_path: Path, service_name: str):
    """为服务创建uv.lock文件"""
    pyproject_path = service_path / "pyproject.toml"
    
    if pyproject_path.exists():
        try:
            # 切换到服务目录
            original_cwd = os.getcwd()
            os.chdir(service_path)
            
            # 运行uv lock
            result = subprocess.run(
                ["uv", "lock"],
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                log_info(f"为 {service_name} 创建uv.lock文件成功")
            else:
                log_warning(f"为 {service_name} 创建uv.lock文件失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            log_warning(f"为 {service_name} 创建uv.lock文件超时")
        except FileNotFoundError:
            log_warning("UV包管理器未安装，跳过uv.lock文件创建")
        finally:
            os.chdir(original_cwd)

def standardize_service(service_relative_path: str):
    """标准化单个服务"""
    service_path = SERVICES_DIR / service_relative_path
    service_name = service_relative_path.split("/")[-1]  # 获取服务名
    
    if not service_path.exists():
        log_warning(f"服务路径不存在: {service_path}")
        return
    
    log_info(f"开始标准化服务: {service_name}")
    
    try:
        # 1. 更新Dockerfile
        update_service_dockerfile(service_path, service_name)
        
        # 2. 更新docker-compose.yml
        update_service_compose(service_path, service_name)
        
        # 3. 移除requirements.txt（如果有pyproject.toml）
        remove_requirements_txt(service_path, service_name)
        
        # 4. 创建uv.lock文件
        create_uv_lock(service_path, service_name)
        
        log_info(f"服务 {service_name} 标准化完成")
        
    except Exception as e:
        log_error(f"标准化服务 {service_name} 时出错: {str(e)}")

def main():
    """主函数"""
    log_info("开始索克生活微服务标准化")
    log_info(f"项目根目录: {PROJECT_ROOT}")
    log_info(f"服务目录: {SERVICES_DIR}")
    
    # 检查UV是否安装
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        log_info("UV包管理器已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        log_warning("UV包管理器未安装，部分功能将跳过")
    
    # 标准化所有服务
    for service_path in SERVICES_TO_STANDARDIZE:
        standardize_service(service_path)
    
    log_info("微服务标准化完成")
    log_info("请检查各服务的配置文件，并根据需要进行调整")

if __name__ == "__main__":
    main() 