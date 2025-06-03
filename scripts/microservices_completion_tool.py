#!/usr/bin/env python3
"""
索克生活平台微服务完成度评估和自动化完善工具

该工具用于：
1. 评估所有微服务的完成度
2. 自动生成缺失的配置文件
3. 标准化项目结构
4. 生成部署配置
5. 创建监控和测试配置
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ServiceStatus:
    """微服务状态数据类"""
    name: str
    path: str
    completion_score: float
    missing_components: List[str]
    has_pyproject: bool
    has_dockerfile: bool
    has_main_module: bool
    has_api_routes: bool
    has_tests: bool
    has_docs: bool
    has_config: bool
    has_deployment: bool
    has_monitoring: bool
    recommendations: List[str]

class MicroserviceCompletionTool:
    """微服务完成度工具"""
    
    def __init__(self, services_root: str = "services"):
        self.services_root = Path(services_root)
        self.template_service = "agent-services/xiaoai-service"
        self.services_status: List[ServiceStatus] = []
        
        # 微服务列表
        self.microservices = [
            "api-gateway",
            "auth-service", 
            "health-data-service",
            "blockchain-service",
            "message-bus",
            "rag-service",
            "user-service",
            "med-knowledge",
            "corn-maze-service",
            "medical-resource-service",
            "accessibility-service",
            "human-review-service",
            "integration-service",
            "suoke-bench-service",
            "a2a-agent-network",
            "agent-services/xiaoai-service",
            "agent-services/xiaoke-service", 
            "agent-services/laoke-service",
            "agent-services/soer-service",
            "diagnostic-services/look-service",
            "diagnostic-services/listen-service",
            "diagnostic-services/inquiry-service",
            "diagnostic-services/palpation-service",
            "diagnostic-services/calculation-service"
        ]
    
    def evaluate_service_completion(self, service_path: Path) -> ServiceStatus:
        """评估单个微服务的完成度"""
        service_name = service_path.name
        if service_path.parent.name != "services":
            service_name = f"{service_path.parent.name}/{service_name}"
        
        # 检查各个组件
        has_pyproject = (service_path / "pyproject.toml").exists()
        has_dockerfile = (service_path / "Dockerfile").exists()
        has_main_module = self._check_main_module(service_path)
        has_api_routes = self._check_api_routes(service_path)
        has_tests = (service_path / "tests").exists() or (service_path / "test").exists()
        has_docs = (service_path / "docs").exists() or (service_path / "README.md").exists()
        has_config = self._check_config(service_path)
        has_deployment = self._check_deployment(service_path)
        has_monitoring = self._check_monitoring(service_path)
        
        # 计算完成度分数
        components = [
            has_pyproject, has_dockerfile, has_main_module, has_api_routes,
            has_tests, has_docs, has_config, has_deployment, has_monitoring
        ]
        completion_score = sum(components) / len(components) * 100
        
        # 识别缺失组件
        missing_components = []
        recommendations = []
        
        if not has_pyproject:
            missing_components.append("pyproject.toml")
            recommendations.append("创建标准化的pyproject.toml配置文件")
        
        if not has_dockerfile:
            missing_components.append("Dockerfile")
            recommendations.append("添加Docker容器化配置")
        
        if not has_main_module:
            missing_components.append("main_module")
            recommendations.append("创建主要业务模块和入口文件")
        
        if not has_api_routes:
            missing_components.append("api_routes")
            recommendations.append("实现API路由和端点")
        
        if not has_tests:
            missing_components.append("tests")
            recommendations.append("添加单元测试和集成测试")
        
        if not has_docs:
            missing_components.append("documentation")
            recommendations.append("完善文档和API说明")
        
        if not has_config:
            missing_components.append("configuration")
            recommendations.append("添加配置管理和环境变量")
        
        if not has_deployment:
            missing_components.append("deployment")
            recommendations.append("创建部署配置和脚本")
        
        if not has_monitoring:
            missing_components.append("monitoring")
            recommendations.append("集成监控和健康检查")
        
        return ServiceStatus(
            name=service_name,
            path=str(service_path),
            completion_score=completion_score,
            missing_components=missing_components,
            has_pyproject=has_pyproject,
            has_dockerfile=has_dockerfile,
            has_main_module=has_main_module,
            has_api_routes=has_api_routes,
            has_tests=has_tests,
            has_docs=has_docs,
            has_config=has_config,
            has_deployment=has_deployment,
            has_monitoring=has_monitoring,
            recommendations=recommendations
        )
    
    def _check_main_module(self, service_path: Path) -> bool:
        """检查是否有主要业务模块"""
        # 检查常见的主模块文件
        main_files = ["main.py", "app.py", "__init__.py"]
        service_name = service_path.name.replace("-", "_")
        
        # 检查根目录的主文件
        for main_file in main_files:
            if (service_path / main_file).exists():
                return True
        
        # 检查服务名称目录下的模块
        service_module_dir = service_path / service_name
        if service_module_dir.exists():
            for main_file in main_files:
                if (service_module_dir / main_file).exists():
                    return True
        
        return False
    
    def _check_api_routes(self, service_path: Path) -> bool:
        """检查是否有API路由定义"""
        # 检查常见的API文件位置
        api_paths = [
            service_path / "api",
            service_path / "routes", 
            service_path / "endpoints"
        ]
        
        for api_path in api_paths:
            if api_path.exists() and any(api_path.iterdir()):
                return True
        
        # 检查服务模块内的API
        service_name = service_path.name.replace("-", "_")
        service_module_dir = service_path / service_name
        if service_module_dir.exists():
            for api_subdir in ["api", "routes", "endpoints"]:
                if (service_module_dir / api_subdir).exists():
                    return True
        
        return False
    
    def _check_config(self, service_path: Path) -> bool:
        """检查配置文件"""
        config_files = [
            "config.py", "settings.py", "env.example", 
            ".env.example", "config.yaml", "config.json"
        ]
        
        for config_file in config_files:
            if (service_path / config_file).exists():
                return True
        
        # 检查config目录
        if (service_path / "config").exists():
            return True
        
        return False
    
    def _check_deployment(self, service_path: Path) -> bool:
        """检查部署配置"""
        deployment_files = [
            "docker-compose.yml", "docker-compose.yaml",
            "Makefile", "deploy.sh"
        ]
        
        for deploy_file in deployment_files:
            if (service_path / deploy_file).exists():
                return True
        
        # 检查deploy目录
        if (service_path / "deploy").exists():
            return True
        
        return False
    
    def _check_monitoring(self, service_path: Path) -> bool:
        """检查监控配置"""
        # 检查pyproject.toml中的监控依赖
        pyproject_file = service_path / "pyproject.toml"
        if pyproject_file.exists():
            try:
                with open(pyproject_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if any(keyword in content for keyword in [
                        "prometheus", "opentelemetry", "sentry", "monitoring"
                    ]):
                        return True
            except Exception:
                pass
        
        return False
    
    def evaluate_all_services(self) -> List[ServiceStatus]:
        """评估所有微服务"""
        print("🔍 开始评估所有微服务的完成度...")
        
        for service_name in self.microservices:
            service_path = self.services_root / service_name
            
            if service_path.exists():
                status = self.evaluate_service_completion(service_path)
                self.services_status.append(status)
                print(f"✅ {service_name}: {status.completion_score:.1f}%")
            else:
                print(f"❌ {service_name}: 服务目录不存在")
        
        return self.services_status
    
    def generate_completion_report(self) -> str:
        """生成完成度报告"""
        if not self.services_status:
            self.evaluate_all_services()
        
        total_services = len(self.services_status)
        avg_completion = sum(s.completion_score for s in self.services_status) / total_services
        
        # 按完成度排序
        sorted_services = sorted(self.services_status, key=lambda x: x.completion_score, reverse=True)
        
        report = f"""
# 索克生活平台微服务完成度报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 总体概况

- **总服务数量**: {total_services}
- **平均完成度**: {avg_completion:.1f}%
- **完全完成服务**: {len([s for s in self.services_status if s.completion_score == 100])}
- **需要完善服务**: {len([s for s in self.services_status if s.completion_score < 100])}

## 服务完成度排名

| 排名 | 服务名称 | 完成度 | 缺失组件数 | 状态 |
|------|----------|--------|------------|------|
"""
        
        for i, service in enumerate(sorted_services, 1):
            status_emoji = "🟢" if service.completion_score == 100 else "🟡" if service.completion_score >= 70 else "🔴"
            report += f"| {i} | {service.name} | {service.completion_score:.1f}% | {len(service.missing_components)} | {status_emoji} |\n"
        
        report += "\n## 详细分析\n\n"
        
        for service in sorted_services:
            if service.completion_score < 100:
                report += f"### {service.name} ({service.completion_score:.1f}%)\n\n"
                report += "**缺失组件:**\n"
                for component in service.missing_components:
                    report += f"- {component}\n"
                report += "\n**改进建议:**\n"
                for recommendation in service.recommendations:
                    report += f"- {recommendation}\n"
                report += "\n"
        
        return report
    
    def auto_complete_service(self, service_name: str) -> bool:
        """自动完善指定的微服务"""
        service_path = self.services_root / service_name
        
        if not service_path.exists():
            print(f"❌ 服务 {service_name} 不存在")
            return False
        
        print(f"🔧 开始自动完善服务: {service_name}")
        
        # 获取服务状态
        status = self.evaluate_service_completion(service_path)
        
        # 创建缺失的组件
        success = True
        
        if not status.has_pyproject:
            success &= self._create_pyproject_toml(service_path, service_name)
        
        if not status.has_dockerfile:
            success &= self._create_dockerfile(service_path, service_name)
        
        if not status.has_main_module:
            success &= self._create_main_module(service_path, service_name)
        
        if not status.has_api_routes:
            success &= self._create_api_routes(service_path, service_name)
        
        if not status.has_tests:
            success &= self._create_tests(service_path, service_name)
        
        if not status.has_config:
            success &= self._create_config(service_path, service_name)
        
        if not status.has_deployment:
            success &= self._create_deployment(service_path, service_name)
        
        return success
    
    def _create_pyproject_toml(self, service_path: Path, service_name: str) -> bool:
        """创建pyproject.toml文件"""
        try:
            # 基于模板创建pyproject.toml
            template_path = self.services_root / self.template_service / "pyproject.toml"
            
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 替换服务名称和描述
                service_display_name = service_name.replace("-", " ").title()
                content = content.replace("xiaoai-service", service_name)
                content = content.replace("小艾智能体服务", f"{service_display_name}服务")
                content = content.replace("xiaoai", service_name.replace("-", "_"))
                
                with open(service_path / "pyproject.toml", 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ 创建 pyproject.toml for {service_name}")
                return True
            else:
                print(f"❌ 模板文件不存在: {template_path}")
                return False
        except Exception as e:
            print(f"❌ 创建 pyproject.toml 失败: {e}")
            return False
    
    def _create_dockerfile(self, service_path: Path, service_name: str) -> bool:
        """创建Dockerfile"""
        try:
            dockerfile_content = f'''# {service_name} Dockerfile
FROM python:3.13.3-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# 安装UV包管理器
RUN pip install uv

# 复制项目文件
COPY pyproject.toml uv.lock ./
COPY {service_name.replace("-", "_")}/ ./{service_name.replace("-", "_")}/

# 安装Python依赖
RUN uv sync --frozen

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "python", "-m", "{service_name.replace("-", "_")}.main"]
'''
            
            with open(service_path / "Dockerfile", 'w', encoding='utf-8') as f:
                f.write(dockerfile_content)
            
            print(f"✅ 创建 Dockerfile for {service_name}")
            return True
        except Exception as e:
            print(f"❌ 创建 Dockerfile 失败: {e}")
            return False
    
    def _create_main_module(self, service_path: Path, service_name: str) -> bool:
        """创建主要业务模块"""
        try:
            module_name = service_name.replace("-", "_")
            module_dir = service_path / module_name
            module_dir.mkdir(exist_ok=True)
            
            # 创建__init__.py
            init_content = f'''"""
{service_name} - 索克生活平台微服务
"""

__version__ = "1.0.0"
__author__ = "Suoke Life Team"
'''
            
            with open(module_dir / "__init__.py", 'w', encoding='utf-8') as f:
                f.write(init_content)
            
            # 创建main.py
            main_content = f'''"""
{service_name} 主入口文件
"""

import uvicorn
from fastapi import FastAPI
from {module_name}.api.main import create_app

def main():
    """主函数"""
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()
'''
            
            with open(module_dir / "main.py", 'w', encoding='utf-8') as f:
                f.write(main_content)
            
            print(f"✅ 创建主模块 for {service_name}")
            return True
        except Exception as e:
            print(f"❌ 创建主模块失败: {e}")
            return False
    
    def _create_api_routes(self, service_path: Path, service_name: str) -> bool:
        """创建API路由"""
        try:
            module_name = service_name.replace("-", "_")
            api_dir = service_path / module_name / "api"
            api_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建API主文件
            api_main_content = f'''"""
{service_name} API主文件
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from {module_name}.api.routes import health, {module_name.split("_")[0]}

def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="{service_name}",
        description="{service_name} API服务",
        version="1.0.0"
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(health.router, prefix="/health", tags=["健康检查"])
    app.include_router({module_name.split("_")[0]}.router, prefix="/api/v1", tags=["{service_name}"])
    
    return app
'''
            
            with open(api_dir / "main.py", 'w', encoding='utf-8') as f:
                f.write(api_main_content)
            
            # 创建路由目录
            routes_dir = api_dir / "routes"
            routes_dir.mkdir(exist_ok=True)
            
            # 创建健康检查路由
            health_route_content = '''"""
健康检查路由
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    message: str

@router.get("/", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        message="Service is running"
    )
'''
            
            with open(routes_dir / "health.py", 'w', encoding='utf-8') as f:
                f.write(health_route_content)
            
            # 创建业务路由
            business_route_content = f'''"""
{service_name} 业务路由
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ServiceResponse(BaseModel):
    message: str
    data: dict = {{}}

@router.get("/", response_model=ServiceResponse)
async def get_service_info():
    """获取服务信息"""
    return ServiceResponse(
        message="{service_name} is running",
        data={{"version": "1.0.0"}}
    )
'''
            
            with open(routes_dir / f"{module_name.split('_')[0]}.py", 'w', encoding='utf-8') as f:
                f.write(business_route_content)
            
            print(f"✅ 创建API路由 for {service_name}")
            return True
        except Exception as e:
            print(f"❌ 创建API路由失败: {e}")
            return False
    
    def _create_tests(self, service_path: Path, service_name: str) -> bool:
        """创建测试文件"""
        try:
            tests_dir = service_path / "tests"
            tests_dir.mkdir(exist_ok=True)
            
            # 创建测试配置
            conftest_content = '''"""
测试配置文件
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

@pytest.fixture
def client():
    """测试客户端"""
    from {}.api.main import create_app
    app = create_app()
    return TestClient(app)
'''.format(service_name.replace("-", "_"))
            
            with open(tests_dir / "conftest.py", 'w', encoding='utf-8') as f:
                f.write(conftest_content)
            
            # 创建API测试
            test_api_content = f'''"""
API测试
"""

def test_health_check(client):
    """测试健康检查"""
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_service_info(client):
    """测试服务信息"""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "{service_name} is running" in data["message"]
'''
            
            with open(tests_dir / "test_api.py", 'w', encoding='utf-8') as f:
                f.write(test_api_content)
            
            print(f"✅ 创建测试文件 for {service_name}")
            return True
        except Exception as e:
            print(f"❌ 创建测试文件失败: {e}")
            return False
    
    def _create_config(self, service_path: Path, service_name: str) -> bool:
        """创建配置文件"""
        try:
            # 创建环境变量示例文件
            env_content = f'''# {service_name} 环境变量配置

# 服务配置
SERVICE_NAME={service_name}
SERVICE_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/{service_name.replace("-", "_")}_db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# API配置
API_HOST=0.0.0.0
API_PORT=8000

# 安全配置
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# 监控配置
ENABLE_METRICS=true
METRICS_PORT=9090
'''
            
            with open(service_path / "env.example", 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            # 创建配置模块
            module_name = service_name.replace("-", "_")
            config_file = service_path / module_name / "config.py"
            config_file.parent.mkdir(exist_ok=True)
            
            config_content = f'''"""
{service_name} 配置管理
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置"""
    
    # 服务配置
    service_name: str = "{service_name}"
    service_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # 数据库配置
    database_url: Optional[str] = None
    
    # Redis配置
    redis_url: str = "redis://localhost:6379/0"
    
    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # 安全配置
    secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # 监控配置
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 全局配置实例
settings = Settings()
'''
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            print(f"✅ 创建配置文件 for {service_name}")
            return True
        except Exception as e:
            print(f"❌ 创建配置文件失败: {e}")
            return False
    
    def _create_deployment(self, service_path: Path, service_name: str) -> bool:
        """创建部署配置"""
        try:
            # 创建docker-compose.yml
            compose_content = f'''version: '3.8'

services:
  {service_name}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - DATABASE_URL=postgresql://user:password@db:5432/{service_name.replace("-", "_")}_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: {service_name.replace("-", "_")}_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
'''
            
            with open(service_path / "docker-compose.yml", 'w', encoding='utf-8') as f:
                f.write(compose_content)
            
            # 创建Makefile
            makefile_content = f'''# {service_name} Makefile

.PHONY: help install dev test build run clean

help:  ## 显示帮助信息
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}}'

install:  ## 安装依赖
	uv sync

dev:  ## 启动开发服务器
	uv run python -m {service_name.replace("-", "_")}.main

test:  ## 运行测试
	uv run pytest tests/ -v

test-cov:  ## 运行测试并生成覆盖率报告
	uv run pytest tests/ --cov={service_name.replace("-", "_")} --cov-report=html

build:  ## 构建Docker镜像
	docker build -t {service_name}:latest .

run:  ## 使用Docker Compose启动服务
	docker-compose up -d

stop:  ## 停止Docker Compose服务
	docker-compose down

clean:  ## 清理临时文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

lint:  ## 代码检查
	uv run ruff check .
	uv run mypy {service_name.replace("-", "_")}/

format:  ## 代码格式化
	uv run ruff format .

health:  ## 健康检查
	curl -f http://localhost:8000/health/ || exit 1
'''
            
            with open(service_path / "Makefile", 'w', encoding='utf-8') as f:
                f.write(makefile_content)
            
            print(f"✅ 创建部署配置 for {service_name}")
            return True
        except Exception as e:
            print(f"❌ 创建部署配置失败: {e}")
            return False
    
    def auto_complete_all_services(self) -> Dict[str, bool]:
        """自动完善所有微服务"""
        print("🚀 开始自动完善所有微服务...")
        
        results = {}
        
        for service_name in self.microservices:
            service_path = self.services_root / service_name
            
            if service_path.exists():
                results[service_name] = self.auto_complete_service(service_name)
            else:
                print(f"⚠️  跳过不存在的服务: {service_name}")
                results[service_name] = False
        
        return results
    
    def save_report(self, filename: str = "microservices_completion_report.md"):
        """保存完成度报告"""
        report = self.generate_completion_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📊 报告已保存到: {filename}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="微服务完成度评估和自动化完善工具")
    parser.add_argument("--evaluate", action="store_true", help="评估所有微服务完成度")
    parser.add_argument("--complete", metavar="SERVICE", help="自动完善指定微服务")
    parser.add_argument("--complete-all", action="store_true", help="自动完善所有微服务")
    parser.add_argument("--report", metavar="FILENAME", default="microservices_completion_report.md", help="生成报告文件名")
    
    args = parser.parse_args()
    
    tool = MicroserviceCompletionTool()
    
    if args.evaluate:
        tool.evaluate_all_services()
        tool.save_report(args.report)
    elif args.complete:
        tool.auto_complete_service(args.complete)
    elif args.complete_all:
        tool.auto_complete_all_services()
        tool.evaluate_all_services()
        tool.save_report(args.report)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 