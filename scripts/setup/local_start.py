#!/usr/bin/env python3
"""
索克生活项目 - 本地简化启动脚本
直接启动应用服务，不依赖Docker基础设施
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class LocalService:
    """本地服务配置"""
    name: str
    path: str
    port: int
    cmd: List[str]
    env: Dict[str, str] = None

class LocalServiceManager:
    """本地服务管理器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.running_processes = {}
        
        # 定义本地服务配置
        self.services = [
            # 核心微服务
            LocalService(
                name="med-knowledge",
                path="services/med-knowledge",
                port=8000,
                cmd=["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
                env={"DATABASE_URL": "sqlite:///./med_knowledge.db"}
            ),
            LocalService(
                name="api-gateway",
                path="services/api-gateway",
                port=8080,
                cmd=["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"],
                env={"DATABASE_URL": "sqlite:///./api_gateway.db"}
            ),
            LocalService(
                name="auth-service",
                path="services/auth-service",
                port=50052,
                cmd=["uv", "run", "python", "-m", "cmd.server"],
                env={"DATABASE_URL": "sqlite:///./auth_service.db", "GRPC_PORT": "50052"}
            ),
            LocalService(
                name="user-service",
                path="services/user-service",
                port=50051,
                cmd=["uv", "run", "python", "-m", "cmd.server"],
                env={"DATABASE_URL": "sqlite:///./user_service.db", "GRPC_PORT": "50051"}
            ),
            LocalService(
                name="health-data-service",
                path="services/health-data-service",
                port=50056,
                cmd=["uv", "run", "python", "-m", "cmd.server"],
                env={"DATABASE_URL": "sqlite:///./health_data.db", "GRPC_PORT": "50056"}
            ),
        ]
    
    def print_banner(self):
        """打印启动横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    索克生活 (Suoke Life)                      ║
║                     本地简化启动器                            ║
║                                                              ║
║  🏥 AI驱动的健康管理平台                                      ║
║  🚀 本地开发模式 - 无需Docker                                 ║
║  💡 使用SQLite数据库                                          ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_prerequisites(self) -> bool:
        """检查前置条件"""
        print("🔍 检查本地启动前置条件...")
        
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
        
        # 检查Python
        try:
            result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ Python: {result.stdout.strip()}")
            else:
                print("  ❌ Python3未安装或不可用")
                return False
        except FileNotFoundError:
            print("  ❌ Python3未安装")
            return False
        
        print("✅ 前置条件检查完成\n")
        return True
    
    def create_logs_dirs(self):
        """创建日志目录"""
        for service in self.services:
            service_path = self.project_root / service.path
            logs_dir = service_path / "logs"
            logs_dir.mkdir(exist_ok=True)
    
    def start_service(self, service: LocalService) -> bool:
        """启动单个服务"""
        service_path = self.project_root / service.path
        
        if not service_path.exists():
            print(f"    ❌ 服务路径不存在: {service_path}")
            return False
        
        if not (service_path / "pyproject.toml").exists():
            print(f"    ❌ 缺少pyproject.toml: {service.name}")
            return False
        
        try:
            print(f"    🚀 启动 {service.name} (端口: {service.port})")
            
            # 设置环境变量
            env = os.environ.copy()
            if service.env:
                env.update(service.env)
            
            # 创建日志文件路径
            log_file = service_path / "logs" / f"{service.name}.log"
            
            # 启动进程
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    service.cmd,
                    cwd=service_path,
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            
            self.running_processes[service.name] = process
            
            # 等待启动
            time.sleep(3)
            
            # 检查进程状态
            if process.poll() is None:
                print(f"      ✅ {service.name} 启动成功 (PID: {process.pid})")
                return True
            else:
                print(f"      ❌ {service.name} 启动失败")
                # 读取日志文件的最后几行
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            print(f"      错误日志: {lines[-1].strip()}")
                except:
                    pass
                return False
                
        except Exception as e:
            print(f"      ❌ {service.name} 启动异常: {str(e)}")
            return False
    
    def start_all_services(self):
        """启动所有服务"""
        print("🚀 开始启动索克生活本地服务...\n")
        
        # 检查前置条件
        if not self.check_prerequisites():
            print("❌ 前置条件检查失败，无法启动服务")
            return False
        
        # 创建日志目录
        self.create_logs_dirs()
        
        print("🔧 启动应用服务...")
        
        successful_services = []
        failed_services = []
        
        # 启动服务
        for service in self.services:
            success = self.start_service(service)
            if success:
                successful_services.append(service.name)
            else:
                failed_services.append(service.name)
            
            # 服务间等待
            time.sleep(2)
        
        # 显示结果
        self.show_startup_summary(successful_services, failed_services)
        
        return len(failed_services) == 0
    
    def show_startup_summary(self, successful_services: List[str], failed_services: List[str]):
        """显示启动总结"""
        total_services = len(successful_services) + len(failed_services)
        
        print(f"\n{'='*60}")
        print("🎉 索克生活本地服务启动完成!")
        print(f"{'='*60}")
        
        print(f"\n📊 启动统计:")
        print(f"  总服务数: {total_services}")
        print(f"  成功启动: {len(successful_services)}")
        print(f"  启动失败: {len(failed_services)}")
        if total_services > 0:
            print(f"  成功率: {len(successful_services)/total_services*100:.1f}%")
        
        if successful_services:
            print(f"\n✅ 成功启动的服务:")
            for service_name in successful_services:
                process = self.running_processes.get(service_name)
                pid = process.pid if process else "N/A"
                service = next((s for s in self.services if s.name == service_name), None)
                port = service.port if service else "N/A"
                print(f"  - {service_name} (PID: {pid}, 端口: {port})")
        
        if failed_services:
            print(f"\n❌ 启动失败的服务:")
            for service_name in failed_services:
                print(f"  - {service_name}")
        
        print(f"\n🌐 服务访问地址:")
        for service_name in successful_services:
            service = next((s for s in self.services if s.name == service_name), None)
            if service:
                if service.name in ["med-knowledge", "api-gateway"]:
                    print(f"  - {service.name}: http://localhost:{service.port}")
                    if service.name == "med-knowledge":
                        print(f"    📚 API文档: http://localhost:{service.port}/docs")
                    elif service.name == "api-gateway":
                        print(f"    🌐 API网关: http://localhost:{service.port}/docs")
                else:
                    print(f"  - {service.name}: gRPC localhost:{service.port}")
        
        print(f"\n📝 日志查看:")
        for service_name in successful_services:
            service = next((s for s in self.services if s.name == service_name), None)
            if service:
                log_path = f"{service.path}/logs/{service.name}.log"
                print(f"  tail -f {log_path}")
        
        print(f"\n🛑 停止所有服务:")
        print(f"  python scripts/local_start.py --stop")
        
        if successful_services:
            print(f"\n🔄 服务正在运行中... (按 Ctrl+C 停止)")
    
    def stop_all_services(self):
        """停止所有服务"""
        print("🛑 停止所有本地服务...")
        
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
        
        print("✅ 所有服务已停止")
    
    def show_service_status(self):
        """显示服务状态"""
        print("📊 索克生活本地服务状态:")
        
        for service_name, process in self.running_processes.items():
            if process.poll() is None:
                service = next((s for s in self.services if s.name == service_name), None)
                port = service.port if service else "N/A"
                print(f"  ✅ {service_name}: 运行中 (PID: {process.pid}, 端口: {port})")
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
    
    parser = argparse.ArgumentParser(description="索克生活本地服务启动管理器")
    parser.add_argument("--stop", action="store_true", help="停止所有服务")
    parser.add_argument("--status", action="store_true", help="显示服务状态")
    
    args = parser.parse_args()
    
    manager = LocalServiceManager(".")
    
    # 注册信号处理
    signal.signal(signal.SIGINT, manager.handle_signal)
    signal.signal(signal.SIGTERM, manager.handle_signal)
    
    manager.print_banner()
    
    if args.stop:
        manager.stop_all_services()
    elif args.status:
        manager.show_service_status()
    else:
        try:
            success = manager.start_all_services()
            
            if success:
                # 保持运行
                while True:
                    time.sleep(10)
            else:
                print("\n❌ 部分服务启动失败，请检查日志")
                
        except KeyboardInterrupt:
            print("\n收到停止信号...")
            manager.stop_all_services()

if __name__ == "__main__":
    main() 