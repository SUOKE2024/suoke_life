#!/usr/bin/env python3
"""
索克生活平台微服务统一管理系统

该系统提供：
1. 统一的微服务启动/停止管理
2. 服务健康检查和监控
3. 批量部署和更新
4. 服务间通信管理
5. 日志聚合和分析
6. 性能监控和报警
"""

import os
import yaml
import asyncio
import aiohttp
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import signal
import sys

@dataclass
class ServiceInfo:
    """微服务信息"""
    name: str
    path: str
    port: int
    health_endpoint: str
    dependencies: List[str]
    status: str = "stopped"
    pid: Optional[int] = None
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"

@dataclass
class ServiceMetrics:
    """服务指标"""
    name: str
    cpu_usage: float
    memory_usage: float
    response_time: float
    request_count: int
    error_rate: float
    uptime: float

class MicroservicesManager:
    """微服务管理器"""
    
    def __init__(self, services_root: str = "services"):
        self.services_root = Path(services_root)
        self.services: Dict[str, ServiceInfo] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = False
        
        # 服务配置
        self.service_configs = {
            "api-gateway": {"port": 8000, "dependencies": []},
            "auth-service": {"port": 8001, "dependencies": []},
            "health-data-service": {"port": 8002, "dependencies": ["auth-service"]},
            "blockchain-service": {"port": 8003, "dependencies": ["auth-service"]},
            "message-bus": {"port": 8004, "dependencies": []},
            "rag-service": {"port": 8005, "dependencies": ["message-bus"]},
            "user-service": {"port": 8006, "dependencies": ["auth-service"]},
            "med-knowledge": {"port": 8007, "dependencies": ["rag-service"]},
            "corn-maze-service": {"port": 8008, "dependencies": ["user-service"]},
            "medical-resource-service": {"port": 8009, "dependencies": ["user-service"]},
            "accessibility-service": {"port": 8010, "dependencies": []},
            "human-review-service": {"port": 8011, "dependencies": ["auth-service"]},
            "integration-service": {"port": 8012, "dependencies": ["message-bus"]},
            "suoke-bench-service": {"port": 8013, "dependencies": []},
            "agent-services/xiaoai-service": {"port": 8015, "dependencies": ["rag-service", "health-data-service"]},
            "agent-services/xiaoke-service": {"port": 8016, "dependencies": ["rag-service", "health-data-service"]},
            "agent-services/laoke-service": {"port": 8017, "dependencies": ["rag-service", "health-data-service"]},
            "agent-services/soer-service": {"port": 8018, "dependencies": ["rag-service", "health-data-service"]},
            "diagnostic-services/look-service": {"port": 8019, "dependencies": ["agent-services/xiaoai-service"]},
            "diagnostic-services/listen-service": {"port": 8020, "dependencies": ["agent-services/xiaoai-service"]},
            "diagnostic-services/inquiry-service": {"port": 8021, "dependencies": ["agent-services/xiaoai-service"]},
            "diagnostic-services/palpation-service": {"port": 8022, "dependencies": ["agent-services/xiaoai-service"]},
            "diagnostic-services/calculation-service": {"port": 8023, "dependencies": ["diagnostic-services/look-service", "diagnostic-services/listen-service", "diagnostic-services/inquiry-service", "diagnostic-services/palpation-service"]},
        }
        
        self._initialize_services()
    
    def _initialize_services(self):
        """初始化服务信息"""
        for service_name, config in self.service_configs.items():
            service_path = self.services_root / service_name
            if service_path.exists():
                self.services[service_name] = ServiceInfo(
                    name=service_name,
                    path=str(service_path),
                    port=config["port"],
                    health_endpoint=f"http://localhost:{config['port']}/health/",
                    dependencies=config["dependencies"]
                )
    
    async def start_service(self, service_name: str) -> bool:
        """启动单个服务"""
        if service_name not in self.services:
            print(f"❌ 服务 {service_name} 不存在")
            return False
        
        service = self.services[service_name]
        
        # 检查依赖服务
        for dep in service.dependencies:
            if dep not in self.services or self.services[dep].status != "running":
                print(f"⚠️  依赖服务 {dep} 未运行，先启动依赖服务")
                if not await self.start_service(dep):
                    print(f"❌ 无法启动依赖服务 {dep}")
                    return False
        
        if service.status == "running":
            print(f"✅ 服务 {service_name} 已在运行")
            return True
        
        print(f"🚀 启动服务: {service_name}")
        
        try:
            # 切换到服务目录
            service_path = Path(service.path)
            
            # 启动服务
            cmd = ["uv", "run", "python", "-m", f"{service_name.replace('-', '_').split('/')[-1]}.main"]
            
            # 设置环境变量
            env = os.environ.copy()
            env["API_PORT"] = str(service.port)
            env["SERVICE_NAME"] = service_name
            
            process = subprocess.Popen(
                cmd,
                cwd=service_path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[service_name] = process
            service.status = "starting"
            service.pid = process.pid
            
            # 等待服务启动
            await self._wait_for_service_ready(service_name)
            
            print(f"✅ 服务 {service_name} 启动成功 (PID: {process.pid}, Port: {service.port})")
            return True
            
        except Exception as e:
            print(f"❌ 启动服务 {service_name} 失败: {e}")
            service.status = "failed"
            return False
    
    async def stop_service(self, service_name: str) -> bool:
        """停止单个服务"""
        if service_name not in self.services:
            print(f"❌ 服务 {service_name} 不存在")
            return False
        
        service = self.services[service_name]
        
        if service.status != "running":
            print(f"✅ 服务 {service_name} 已停止")
            return True
        
        print(f"🛑 停止服务: {service_name}")
        
        try:
            if service_name in self.processes:
                process = self.processes[service_name]
                process.terminate()
                
                # 等待进程结束
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                
                del self.processes[service_name]
            
            service.status = "stopped"
            service.pid = None
            
            print(f"✅ 服务 {service_name} 已停止")
            return True
            
        except Exception as e:
            print(f"❌ 停止服务 {service_name} 失败: {e}")
            return False
    
    async def _wait_for_service_ready(self, service_name: str, timeout: int = 30):
        """等待服务就绪"""
        service = self.services[service_name]
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(service.health_endpoint, timeout=5) as response:
                        if response.status == 200:
                            service.status = "running"
                            service.health_status = "healthy"
                            service.last_health_check = datetime.now()
                            return
            except:
                pass
            
            await asyncio.sleep(1)
        
        service.status = "failed"
        raise Exception(f"服务 {service_name} 启动超时")
    
    async def health_check(self, service_name: str) -> bool:
        """健康检查"""
        if service_name not in self.services:
            return False
        
        service = self.services[service_name]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(service.health_endpoint, timeout=5) as response:
                    if response.status == 200:
                        service.health_status = "healthy"
                        service.last_health_check = datetime.now()
                        return True
                    else:
                        service.health_status = "unhealthy"
                        return False
        except:
            service.health_status = "unreachable"
            return False
    
    async def health_check_all(self) -> Dict[str, bool]:
        """检查所有服务健康状态"""
        results = {}
        
        tasks = []
        for service_name in self.services:
            if self.services[service_name].status == "running":
                tasks.append(self.health_check(service_name))
            else:
                results[service_name] = False
        
        if tasks:
            health_results = await asyncio.gather(*tasks, return_exceptions=True)
            running_services = [name for name, service in self.services.items() if service.status == "running"]
            
            for i, result in enumerate(health_results):
                if isinstance(result, bool):
                    results[running_services[i]] = result
                else:
                    results[running_services[i]] = False
        
        return results
    
    async def start_all_services(self) -> bool:
        """按依赖顺序启动所有服务"""
        print("🚀 开始启动所有微服务...")
        
        # 拓扑排序，按依赖顺序启动
        started = set()
        to_start = set(self.services.keys())
        
        while to_start:
            # 找到没有未满足依赖的服务
            ready_to_start = []
            for service_name in to_start:
                service = self.services[service_name]
                if all(dep in started for dep in service.dependencies):
                    ready_to_start.append(service_name)
            
            if not ready_to_start:
                print("❌ 检测到循环依赖，无法启动所有服务")
                return False
            
            # 并行启动就绪的服务
            tasks = [self.start_service(name) for name in ready_to_start]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                service_name = ready_to_start[i]
                if isinstance(result, bool) and result:
                    started.add(service_name)
                    to_start.remove(service_name)
                else:
                    print(f"❌ 启动服务 {service_name} 失败")
                    return False
        
        print("✅ 所有微服务启动完成")
        return True
    
    async def stop_all_services(self) -> bool:
        """停止所有服务"""
        print("🛑 开始停止所有微服务...")
        
        # 反向依赖顺序停止
        running_services = [name for name, service in self.services.items() if service.status == "running"]
        
        tasks = [self.stop_service(name) for name in running_services]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success = all(isinstance(result, bool) and result for result in results)
        
        if success:
            print("✅ 所有微服务已停止")
        else:
            print("⚠️  部分服务停止失败")
        
        return success
    
    def get_service_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有服务状态"""
        status = {}
        for name, service in self.services.items():
            status[name] = {
                "status": service.status,
                "port": service.port,
                "health_status": service.health_status,
                "last_health_check": service.last_health_check.isoformat() if service.last_health_check else None,
                "pid": service.pid,
                "dependencies": service.dependencies
            }
        return status
    
    async def monitor_services(self, interval: int = 30):
        """持续监控服务"""
        print(f"📊 开始监控服务 (间隔: {interval}秒)")
        
        self.running = True
        
        while self.running:
            try:
                health_results = await self.health_check_all()
                
                print(f"\n📊 服务健康检查报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 60)
                
                for service_name, is_healthy in health_results.items():
                    service = self.services[service_name]
                    status_emoji = "🟢" if is_healthy else "🔴"
                    print(f"{status_emoji} {service_name:30} | Port: {service.port:5} | Status: {service.status:8} | Health: {service.health_status}")
                
                # 检查失败的服务
                failed_services = [name for name, healthy in health_results.items() if not healthy]
                if failed_services:
                    print(f"\n⚠️  检测到 {len(failed_services)} 个服务异常:")
                    for service_name in failed_services:
                        print(f"   - {service_name}")
                
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n🛑 监控已停止")
                break
            except Exception as e:
                print(f"❌ 监控过程中出错: {e}")
                await asyncio.sleep(interval)
    
    def generate_docker_compose(self) -> str:
        """生成Docker Compose配置"""
        compose = {
            "version": "3.8",
            "services": {},
            "networks": {
                "suoke-network": {
                    "driver": "bridge"
                }
            },
            "volumes": {
                "postgres_data": {},
                "redis_data": {},
                "logs_data": {}
            }
        }
        
        # 添加基础设施服务
        compose["services"]["postgres"] = {
            "image": "postgres:15",
            "environment": {
                "POSTGRES_DB": "suoke_db",
                "POSTGRES_USER": "suoke",
                "POSTGRES_PASSWORD": "suoke123"
            },
            "volumes": ["postgres_data:/var/lib/postgresql/data"],
            "ports": ["5432:5432"],
            "networks": ["suoke-network"]
        }
        
        compose["services"]["redis"] = {
            "image": "redis:7-alpine",
            "volumes": ["redis_data:/data"],
            "ports": ["6379:6379"],
            "networks": ["suoke-network"]
        }
        
        # 添加微服务
        for service_name, service in self.services.items():
            service_key = service_name.replace("/", "-")
            
            compose["services"][service_key] = {
                "build": f"./services/{service_name}",
                "ports": [f"{service.port}:8000"],
                "environment": {
                    "DATABASE_URL": "postgresql://suoke:suoke123@postgres:5432/suoke_db",
                    "REDIS_URL": "redis://redis:6379/0",
                    "SERVICE_NAME": service_name,
                    "API_PORT": "8000"
                },
                "depends_on": ["postgres", "redis"] + [dep.replace("/", "-") for dep in service.dependencies],
                "volumes": ["logs_data:/app/logs"],
                "networks": ["suoke-network"],
                "restart": "unless-stopped"
            }
        
        return yaml.dump(compose, default_flow_style=False, allow_unicode=True)
    
    def save_docker_compose(self, filename: str = "docker-compose.microservices.yml"):
        """保存Docker Compose配置"""
        compose_content = self.generate_docker_compose()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(compose_content)
        
        print(f"📄 Docker Compose配置已保存到: {filename}")
    
    async def deploy_with_docker(self):
        """使用Docker部署所有服务"""
        print("🐳 开始Docker部署...")
        
        # 生成Docker Compose文件
        self.save_docker_compose()
        
        try:
            # 构建和启动服务
            subprocess.run(["docker-compose", "-f", "docker-compose.microservices.yml", "up", "-d", "--build"], check=True)
            print("✅ Docker部署完成")
            
            # 等待服务启动
            await asyncio.sleep(30)
            
            # 检查服务状态
            print("📊 检查Docker服务状态...")
            result = subprocess.run(["docker-compose", "-f", "docker-compose.microservices.yml", "ps"], 
                                  capture_output=True, text=True)
            print(result.stdout)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker部署失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        print("🧹 清理资源...")
        
        # 停止所有进程
        for service_name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                    process.wait()
                except:
                    pass
        
        self.processes.clear()
        self.running = False

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="索克生活平台微服务管理系统")
    parser.add_argument("--start", action="store_true", help="启动所有微服务")
    parser.add_argument("--stop", action="store_true", help="停止所有微服务")
    parser.add_argument("--status", action="store_true", help="查看服务状态")
    parser.add_argument("--monitor", action="store_true", help="监控服务")
    parser.add_argument("--health", action="store_true", help="健康检查")
    parser.add_argument("--docker", action="store_true", help="Docker部署")
    parser.add_argument("--compose", action="store_true", help="生成Docker Compose文件")
    parser.add_argument("--service", metavar="SERVICE", help="操作指定服务")
    parser.add_argument("--interval", type=int, default=30, help="监控间隔(秒)")
    
    args = parser.parse_args()
    
    manager = MicroservicesManager()
    
    # 设置信号处理
    def signal_handler(signum, frame):
        print("\n🛑 收到停止信号，正在清理...")
        manager.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if args.start:
            if args.service:
                await manager.start_service(args.service)
            else:
                await manager.start_all_services()
        
        elif args.stop:
            if args.service:
                await manager.stop_service(args.service)
            else:
                await manager.stop_all_services()
        
        elif args.status:
            status = manager.get_service_status()
            print("\n📊 微服务状态报告")
            print("=" * 80)
            for name, info in status.items():
                status_emoji = "🟢" if info["status"] == "running" else "🔴"
                print(f"{status_emoji} {name:30} | Port: {info['port']:5} | Status: {info['status']:8} | Health: {info['health_status']:10}")
        
        elif args.health:
            health_results = await manager.health_check_all()
            print("\n🏥 服务健康检查结果")
            print("=" * 50)
            for name, is_healthy in health_results.items():
                status_emoji = "🟢" if is_healthy else "🔴"
                print(f"{status_emoji} {name:30} | {'健康' if is_healthy else '异常'}")
        
        elif args.monitor:
            await manager.monitor_services(args.interval)
        
        elif args.docker:
            await manager.deploy_with_docker()
        
        elif args.compose:
            manager.save_docker_compose()
        
        else:
            parser.print_help()
    
    finally:
        manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 