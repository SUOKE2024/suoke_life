#!/usr/bin/env python3
"""
索克生活项目 - 统一微服务启动脚本
支持启动所有微服务，包括基础设施、核心服务、智能体服务和诊断服务
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class ServiceConfig:
    """服务配置"""
    name: str
    path: str
    port: int
    type: str  # 'uv', 'docker', 'docker-compose'
    dependencies: List[str] = None
    health_check: str = None
    startup_time: int = 30  # 启动等待时间（秒）

class SuokeServiceManager:
    """索克生活服务管理器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.services_dir = self.project_root / "services"
        self.running_processes = {}
        self.service_status = {}
        
        # 定义所有服务配置
        self.services = {
            # 基础设施服务
            "infrastructure": [
                ServiceConfig("postgres", "deploy/docker", 5432, "docker-compose", health_check="pg_isready"),
                ServiceConfig("redis", "deploy/docker", 6379, "docker-compose", health_check="redis-cli ping"),
                ServiceConfig("consul", "deploy/docker", 8500, "docker-compose", health_check="curl -f http://localhost:8500/v1/status/leader"),
            ],
            
            # 核心微服务
            "core": [
                ServiceConfig("auth-service", "services/auth-service", 50052, "uv", ["postgres", "redis"]),
                ServiceConfig("api-gateway", "services/api-gateway", 8080, "uv", ["auth-service"]),
                ServiceConfig("user-service", "services/user-service", 50051, "uv", ["postgres", "redis"]),
                ServiceConfig("blockchain-service", "services/blockchain-service", 50055, "uv", ["postgres"]),
                ServiceConfig("health-data-service", "services/health-data-service", 50056, "uv", ["postgres", "redis"]),
                ServiceConfig("message-bus", "services/message-bus", 50058, "uv", ["redis"]),
                ServiceConfig("rag-service", "services/rag-service", 50059, "uv", ["postgres"]),
                ServiceConfig("integration-service", "services/integration-service", 8090, "uv", ["postgres", "redis"]),
                ServiceConfig("med-knowledge", "services/med-knowledge", 8000, "uv", ["postgres"]),
                ServiceConfig("corn-maze-service", "services/corn-maze-service", 50057, "uv"),
            ],
            
            # 智能体服务
            "agents": [
                ServiceConfig("xiaoai-service", "services/agent-services/xiaoai-service", 50053, "uv", ["postgres", "redis"]),
                ServiceConfig("xiaoke-service", "services/agent-services/xiaoke-service", 50054, "uv", ["postgres", "redis"]),
                ServiceConfig("laoke-service", "services/agent-services/laoke-service", 9000, "uv", ["postgres", "redis"]),
                ServiceConfig("soer-service", "services/agent-services/soer-service", 50060, "uv", ["postgres", "redis"]),
            ],
            
            # 诊断服务
            "diagnostic": [
                ServiceConfig("inquiry-service", "services/diagnostic-services/inquiry-service", 50052, "uv", ["postgres"]),
                ServiceConfig("look-service", "services/diagnostic-services/look-service", 50051, "uv", ["postgres"]),
                ServiceConfig("listen-service", "services/diagnostic-services/listen-service", 50052, "uv", ["postgres"]),
                ServiceConfig("palpation-service", "services/diagnostic-services/palpation-service", 8000, "uv", ["postgres"]),
            ],
            
            # 其他服务
            "others": [
                ServiceConfig("medical-resource-service", "services/medical-resource-service", 9084, "uv", ["postgres", "redis"]),
                ServiceConfig("suoke-bench-service", "services/suoke-bench-service", 8080, "uv", ["postgres"]),
                ServiceConfig("accessibility-service", "services/accessibility-service", 8080, "uv", ["postgres"]),
            ]
        }
    
    def print_banner(self):
        """打印启动横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    索克生活 (Suoke Life)                      ║
║                   微服务统一启动管理器                        ║
║                                                              ║
║  🏥 AI驱动的健康管理平台                                      ║
║  🤖 四大智能体：小艾、小克、老克、索儿                        ║
║  🔬 中医辨证 + 现代预防医学                                   ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_prerequisites(self) -> bool:
        """检查启动前置条件"""
        print("🔍 检查启动前置条件...")
        
        # 检查uv
        try:
            result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ uv: {result.stdout.strip()}")
            else:
                print("  ❌ uv未安装或不可用")
                return False
        except FileNotFoundError:
            print("  ❌ uv未安装")
            return False
        
        # 检查Docker
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ Docker: {result.stdout.strip()}")
            else:
                print("  ❌ Docker未安装或不可用")
                return False
        except FileNotFoundError:
            print("  ❌ Docker未安装")
            return False
        
        # 检查Docker Compose
        try:
            result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ Docker Compose: {result.stdout.strip()}")
            else:
                print("  ❌ Docker Compose未安装或不可用")
                return False
        except FileNotFoundError:
            print("  ❌ Docker Compose未安装")
            return False
        
        print("✅ 前置条件检查完成\n")
        return True
    
    def create_infrastructure_compose(self):
        """创建基础设施Docker Compose文件"""
        compose_dir = self.project_root / "deploy" / "docker"
        compose_dir.mkdir(parents=True, exist_ok=True)
        
        compose_content = """version: '3.8'

services:
  # PostgreSQL数据库
  postgres:
    image: postgres:15
    container_name: suoke-postgres
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=suoke_life
      - POSTGRES_USER=suoke
      - POSTGRES_PASSWORD=suoke123
      - POSTGRES_MULTIPLE_DATABASES=auth_service,user_service,health_data,blockchain_service,rag_service,integration_service,med_knowledge,xiaoai_service,xiaoke_service,laoke_service,soer_service,inquiry_service,look_service,listen_service,palpation_service,medical_resources,suoke_bench,accessibility_service
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    networks:
      - suoke-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U suoke"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: suoke-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    command: redis-server --requirepass suoke123
    volumes:
      - redis_data:/data
    networks:
      - suoke-network
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "suoke123", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  # Consul服务发现
  consul:
    image: consul:1.15
    container_name: suoke-consul
    restart: unless-stopped
    ports:
      - "8500:8500"
    command: agent -server -bootstrap -ui -client=0.0.0.0
    volumes:
      - consul_data:/consul/data
    networks:
      - suoke-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8500/v1/status/leader"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Prometheus监控
  prometheus:
    image: prom/prometheus:latest
    container_name: suoke-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - suoke-network

  # Grafana仪表板
  grafana:
    image: grafana/grafana:latest
    container_name: suoke-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=suoke123
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - suoke-network

networks:
  suoke-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  consul_data:
  prometheus_data:
  grafana_data:
"""
        
        compose_file = compose_dir / "docker-compose.yml"
        with open(compose_file, 'w', encoding='utf-8') as f:
            f.write(compose_content)
        
        # 创建PostgreSQL初始化脚本
        init_scripts_dir = compose_dir / "init-scripts"
        init_scripts_dir.mkdir(exist_ok=True)
        
        init_script = """#!/bin/bash
set -e

# 创建多个数据库
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE auth_service;
    CREATE DATABASE user_service;
    CREATE DATABASE health_data;
    CREATE DATABASE blockchain_service;
    CREATE DATABASE rag_service;
    CREATE DATABASE integration_service;
    CREATE DATABASE med_knowledge;
    CREATE DATABASE xiaoai_service;
    CREATE DATABASE xiaoke_service;
    CREATE DATABASE laoke_service;
    CREATE DATABASE soer_service;
    CREATE DATABASE inquiry_service;
    CREATE DATABASE look_service;
    CREATE DATABASE listen_service;
    CREATE DATABASE palpation_service;
    CREATE DATABASE medical_resources;
    CREATE DATABASE suoke_bench;
    CREATE DATABASE accessibility_service;
EOSQL
"""
        
        init_script_file = init_scripts_dir / "01-create-databases.sh"
        with open(init_script_file, 'w', encoding='utf-8') as f:
            f.write(init_script)
        
        # 设置执行权限
        os.chmod(init_script_file, 0o755)
        
        # 创建Prometheus配置
        prometheus_config = """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'suoke-services'
    static_configs:
      - targets: ['localhost:8080', 'localhost:50051', 'localhost:50052', 'localhost:50053', 'localhost:50054', 'localhost:50055', 'localhost:50056', 'localhost:50057', 'localhost:50058', 'localhost:50059', 'localhost:50060', 'localhost:8000', 'localhost:8090', 'localhost:9000', 'localhost:9084']
"""
        
        prometheus_file = compose_dir / "prometheus.yml"
        with open(prometheus_file, 'w', encoding='utf-8') as f:
            f.write(prometheus_config)
        
        print(f"✅ 基础设施配置已创建: {compose_file}")
    
    def start_infrastructure(self) -> bool:
        """启动基础设施服务"""
        print("🚀 启动基础设施服务...")
        
        compose_dir = self.project_root / "deploy" / "docker"
        if not (compose_dir / "docker-compose.yml").exists():
            self.create_infrastructure_compose()
        
        try:
            # 启动基础设施
            result = subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=compose_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print("  ✅ 基础设施服务启动成功")
                
                # 等待服务就绪
                print("  ⏳ 等待基础设施服务就绪...")
                time.sleep(15)
                
                # 检查服务状态
                self.check_infrastructure_health()
                return True
            else:
                print(f"  ❌ 基础设施启动失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("  ⏰ 基础设施启动超时")
            return False
        except Exception as e:
            print(f"  ❌ 基础设施启动异常: {str(e)}")
            return False
    
    def check_infrastructure_health(self):
        """检查基础设施健康状态"""
        print("  🔍 检查基础设施健康状态...")
        
        # 检查PostgreSQL
        try:
            result = subprocess.run(
                ["docker", "exec", "suoke-postgres", "pg_isready", "-U", "suoke"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print("    ✅ PostgreSQL: 健康")
            else:
                print("    ⚠️  PostgreSQL: 未就绪")
        except:
            print("    ❌ PostgreSQL: 检查失败")
        
        # 检查Redis
        try:
            result = subprocess.run(
                ["docker", "exec", "suoke-redis", "redis-cli", "-a", "suoke123", "ping"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if "PONG" in result.stdout:
                print("    ✅ Redis: 健康")
            else:
                print("    ⚠️  Redis: 未就绪")
        except:
            print("    ❌ Redis: 检查失败")
        
        # 检查Consul
        try:
            result = subprocess.run(
                ["curl", "-f", "http://localhost:8500/v1/status/leader"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print("    ✅ Consul: 健康")
            else:
                print("    ⚠️  Consul: 未就绪")
        except:
            print("    ❌ Consul: 检查失败")
    
    def start_service_with_uv(self, service: ServiceConfig) -> bool:
        """使用uv启动单个服务"""
        service_path = self.project_root / service.path
        
        if not service_path.exists():
            print(f"    ❌ 服务路径不存在: {service_path}")
            return False
        
        if not (service_path / "pyproject.toml").exists():
            print(f"    ❌ 缺少pyproject.toml: {service.name}")
            return False
        
        try:
            # 启动服务
            print(f"    🚀 启动 {service.name} (端口: {service.port})")
            
            # 创建启动命令
            if service.name in ["api-gateway", "med-knowledge", "palpation-service"]:
                cmd = ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(service.port)]
            elif "service" in service.name:
                cmd = ["uv", "run", "python", "-m", "cmd.server"]
            else:
                cmd = ["uv", "run", "python", "main.py"]
            
            # 启动进程
            process = subprocess.Popen(
                cmd,
                cwd=service_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.running_processes[service.name] = process
            
            # 等待启动
            time.sleep(service.startup_time)
            
            # 检查进程状态
            if process.poll() is None:
                print(f"      ✅ {service.name} 启动成功 (PID: {process.pid})")
                self.service_status[service.name] = "running"
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"      ❌ {service.name} 启动失败")
                print(f"      错误: {stderr[:200]}...")
                self.service_status[service.name] = "failed"
                return False
                
        except Exception as e:
            print(f"      ❌ {service.name} 启动异常: {str(e)}")
            self.service_status[service.name] = "error"
            return False
    
    def start_service_group(self, group_name: str, services: List[ServiceConfig]) -> Dict[str, bool]:
        """启动服务组"""
        print(f"\n🔧 启动 {group_name} 服务组...")
        results = {}
        
        # 使用线程池并行启动服务
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_service = {}
            
            for service in services:
                if service.type == "uv":
                    future = executor.submit(self.start_service_with_uv, service)
                    future_to_service[future] = service
            
            # 收集结果
            for future in as_completed(future_to_service):
                service = future_to_service[future]
                try:
                    success = future.result()
                    results[service.name] = success
                except Exception as e:
                    print(f"    ❌ {service.name} 启动异常: {str(e)}")
                    results[service.name] = False
        
        # 统计结果
        successful = sum(results.values())
        total = len(results)
        print(f"  📊 {group_name} 启动完成: {successful}/{total} 成功")
        
        return results
    
    def start_all_services(self):
        """启动所有服务"""
        print("🚀 开始启动索克生活所有微服务...\n")
        
        # 检查前置条件
        if not self.check_prerequisites():
            print("❌ 前置条件检查失败，无法启动服务")
            return False
        
        # 启动基础设施
        if not self.start_infrastructure():
            print("❌ 基础设施启动失败，无法继续")
            return False
        
        all_results = {}
        
        # 按顺序启动各服务组
        service_groups = [
            ("核心微服务", self.services["core"]),
            ("智能体服务", self.services["agents"]),
            ("诊断服务", self.services["diagnostic"]),
            ("其他服务", self.services["others"])
        ]
        
        for group_name, services in service_groups:
            group_results = self.start_service_group(group_name, services)
            all_results.update(group_results)
            
            # 服务组间等待
            time.sleep(5)
        
        # 显示最终结果
        self.show_startup_summary(all_results)
        
        return True
    
    def show_startup_summary(self, results: Dict[str, bool]):
        """显示启动总结"""
        successful_services = [name for name, success in results.items() if success]
        failed_services = [name for name, success in results.items() if not success]
        
        print(f"\n{'='*60}")
        print("🎉 索克生活微服务启动完成!")
        print(f"{'='*60}")
        
        print(f"\n📊 启动统计:")
        print(f"  总服务数: {len(results)}")
        print(f"  成功启动: {len(successful_services)}")
        print(f"  启动失败: {len(failed_services)}")
        print(f"  成功率: {len(successful_services)/len(results)*100:.1f}%")
        
        if successful_services:
            print(f"\n✅ 成功启动的服务:")
            for service in successful_services:
                process = self.running_processes.get(service)
                pid = process.pid if process else "N/A"
                print(f"  - {service} (PID: {pid})")
        
        if failed_services:
            print(f"\n❌ 启动失败的服务:")
            for service in failed_services:
                print(f"  - {service}")
        
        print(f"\n🌐 服务访问地址:")
        print(f"  - API网关: http://localhost:8080")
        print(f"  - Consul UI: http://localhost:8500")
        print(f"  - Grafana: http://localhost:3000 (admin/suoke123)")
        print(f"  - Prometheus: http://localhost:9090")
        print(f"  - PostgreSQL: localhost:5432 (suoke/suoke123)")
        print(f"  - Redis: localhost:6379 (密码: suoke123)")
        
        print(f"\n📝 日志查看:")
        print(f"  docker-compose -f deploy/docker/docker-compose.yml logs -f")
        print(f"  或查看各服务目录下的logs文件夹")
        
        print(f"\n🛑 停止所有服务:")
        print(f"  python scripts/start_all_services.py --stop")
    
    def stop_all_services(self):
        """停止所有服务"""
        print("🛑 停止所有索克生活微服务...")
        
        # 停止uv启动的服务
        for service_name, process in self.running_processes.items():
            try:
                print(f"  🛑 停止 {service_name}...")
                process.terminate()
                process.wait(timeout=10)
                print(f"    ✅ {service_name} 已停止")
            except subprocess.TimeoutExpired:
                print(f"    ⚠️  强制终止 {service_name}")
                process.kill()
            except Exception as e:
                print(f"    ❌ 停止 {service_name} 失败: {str(e)}")
        
        # 停止基础设施
        compose_dir = self.project_root / "deploy" / "docker"
        if (compose_dir / "docker-compose.yml").exists():
            try:
                subprocess.run(
                    ["docker-compose", "down"],
                    cwd=compose_dir,
                    timeout=60
                )
                print("  ✅ 基础设施服务已停止")
            except Exception as e:
                print(f"  ❌ 停止基础设施失败: {str(e)}")
        
        print("✅ 所有服务已停止")
    
    def show_service_status(self):
        """显示服务状态"""
        print("📊 索克生活微服务状态:")
        
        # 检查基础设施
        print("\n🏗️  基础设施:")
        try:
            result = subprocess.run(
                ["docker-compose", "ps"],
                cwd=self.project_root / "deploy" / "docker",
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(result.stdout)
        except:
            print("  ❌ 无法获取基础设施状态")
        
        # 检查应用服务
        print("\n🚀 应用服务:")
        for service_name, process in self.running_processes.items():
            if process.poll() is None:
                print(f"  ✅ {service_name}: 运行中 (PID: {process.pid})")
            else:
                print(f"  ❌ {service_name}: 已停止")
    
    def handle_signal(self, signum, frame):
        """处理信号"""
        print(f"\n收到信号 {signum}，正在停止所有服务...")
        self.stop_all_services()
        sys.exit(0)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="索克生活微服务启动管理器")
    parser.add_argument("--stop", action="store_true", help="停止所有服务")
    parser.add_argument("--status", action="store_true", help="显示服务状态")
    parser.add_argument("--infrastructure-only", action="store_true", help="仅启动基础设施")
    
    args = parser.parse_args()
    
    manager = SuokeServiceManager(".")
    
    # 注册信号处理
    signal.signal(signal.SIGINT, manager.handle_signal)
    signal.signal(signal.SIGTERM, manager.handle_signal)
    
    manager.print_banner()
    
    if args.stop:
        manager.stop_all_services()
    elif args.status:
        manager.show_service_status()
    elif args.infrastructure_only:
        manager.start_infrastructure()
    else:
        try:
            manager.start_all_services()
            
            # 保持运行
            print("\n🔄 服务正在运行中... (按 Ctrl+C 停止)")
            while True:
                time.sleep(10)
                
        except KeyboardInterrupt:
            print("\n收到停止信号...")
            manager.stop_all_services()

if __name__ == "__main__":
    main() 