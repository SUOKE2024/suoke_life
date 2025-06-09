#!/usr/bin/env python3
"""
索克生活微服务合并工具
根据分析结果实施服务合并
"""

import os
import json
import shutil
import subprocess
from pathlib import Path

class ServiceMerger:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.services_dir = self.project_root / "services"
        self.backup_dir = self.project_root / "backup" / "services"
        
    def load_analysis(self):
        """加载分析结果"""
        analysis_file = self.project_root / "service_analysis.json"
        if not analysis_file.exists():
            print("❌ 请先运行 scripts/analyze-services.py")
            return None
        
        with open(analysis_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_backup(self, services_to_merge):
        """创建备份"""
        print("📦 创建服务备份...")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        for service_name in services_to_merge:
            service_path = self.services_dir / service_name
            if service_path.exists():
                backup_path = self.backup_dir / service_name
                if backup_path.exists():
                    shutil.rmtree(backup_path)
                shutil.copytree(service_path, backup_path)
                print(f"  ✅ 备份: {service_name}")
    
    def merge_auth_services(self):
        """合并认证和用户服务"""
        print("\n🔄 合并认证和用户服务...")
        
        auth_service = self.services_dir / "auth-service"
        user_service = self.services_dir / "user-service"
        target_service = self.services_dir / "user-management-service"
        
        if not auth_service.exists() or not user_service.exists():
            print("❌ 源服务不存在")
            return False
        
        # 创建备份
        self.create_backup(["auth-service", "user-service"])
        
        # 创建新的合并服务目录
        target_service.mkdir(exist_ok=True)
        
        # 合并目录结构
        self._merge_service_structure(
            [auth_service, user_service], 
            target_service,
            "user-management-service"
        )
        
        print("✅ 认证和用户服务合并完成")
        return True
    
    def merge_data_services(self):
        """合并数据服务"""
        print("\n🔄 合并数据服务...")
        
        database_service = self.services_dir / "database"
        health_data_service = self.services_dir / "health-data-service"
        target_service = self.services_dir / "unified-health-data-service"
        
        if not health_data_service.exists():
            print("❌ 健康数据服务不存在")
            return False
        
        # 创建备份
        services_to_backup = ["health-data-service"]
        if database_service.exists():
            services_to_backup.append("database")
        
        self.create_backup(services_to_backup)
        
        # 创建新的合并服务目录
        target_service.mkdir(exist_ok=True)
        
        # 合并目录结构
        source_services = [health_data_service]
        if database_service.exists():
            source_services.append(database_service)
            
        self._merge_service_structure(
            source_services, 
            target_service,
            "unified-health-data-service"
        )
        
        print("✅ 数据服务合并完成")
        return True
    
    def _merge_service_structure(self, source_services, target_service, service_name):
        """合并服务目录结构"""
        
        # 创建基本目录结构
        dirs_to_create = [
            "api", "config", "deploy", "docs", "tests", "utils",
            service_name.replace("-", "_")
        ]
        
        for dir_name in dirs_to_create:
            (target_service / dir_name).mkdir(exist_ok=True)
        
        # 合并文件
        for source_service in source_services:
            print(f"  📁 合并 {source_service.name}...")
            
            # 复制Python代码
            source_code_dir = source_service / source_service.name.replace("-", "_")
            if source_code_dir.exists():
                target_code_dir = target_service / service_name.replace("-", "_") / source_service.name.replace("-", "_")
                target_code_dir.mkdir(parents=True, exist_ok=True)
                self._copy_directory_contents(source_code_dir, target_code_dir)
            
            # 复制API定义
            source_api = source_service / "api"
            if source_api.exists():
                target_api = target_service / "api" / source_service.name
                target_api.mkdir(parents=True, exist_ok=True)
                self._copy_directory_contents(source_api, target_api)
            
            # 复制配置文件
            source_config = source_service / "config"
            if source_config.exists():
                target_config = target_service / "config" / source_service.name
                target_config.mkdir(parents=True, exist_ok=True)
                self._copy_directory_contents(source_config, target_config)
            
            # 复制测试文件
            for test_dir in ["test", "tests"]:
                source_test = source_service / test_dir
                if source_test.exists():
                    target_test = target_service / "tests" / source_service.name
                    target_test.mkdir(parents=True, exist_ok=True)
                    self._copy_directory_contents(source_test, target_test)
            
            # 复制部署配置
            source_deploy = source_service / "deploy"
            if source_deploy.exists():
                target_deploy = target_service / "deploy" / source_service.name
                target_deploy.mkdir(parents=True, exist_ok=True)
                self._copy_directory_contents(source_deploy, target_deploy)
            
            # 复制Dockerfile
            source_dockerfile = source_service / "Dockerfile"
            if source_dockerfile.exists():
                target_dockerfile = target_service / f"Dockerfile.{source_service.name}"
                shutil.copy2(source_dockerfile, target_dockerfile)
            
            # 复制requirements.txt
            source_requirements = source_service / "requirements.txt"
            if source_requirements.exists():
                target_requirements = target_service / f"requirements.{source_service.name}.txt"
                shutil.copy2(source_requirements, target_requirements)
        
        # 创建合并后的主要文件
        self._create_merged_files(target_service, service_name, source_services)
    
    def _copy_directory_contents(self, source, target):
        """复制目录内容"""
        try:
            if source.exists() and source.is_dir():
                for item in source.iterdir():
                    if item.is_file():
                        shutil.copy2(item, target / item.name)
                    elif item.is_dir():
                        target_subdir = target / item.name
                        target_subdir.mkdir(exist_ok=True)
                        self._copy_directory_contents(item, target_subdir)
        except Exception as e:
            print(f"    ⚠️ 复制失败 {source} -> {target}: {e}")
    
    def _create_merged_files(self, target_service, service_name, source_services):
        """创建合并后的主要文件"""
        
        # 创建主Dockerfile
        dockerfile_content = f"""FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
"""
        
        for source_service in source_services:
            req_file = f"requirements.{source_service.name}.txt"
            if (target_service / req_file).exists():
                dockerfile_content += f"COPY {req_file} .\n"
        
        dockerfile_content += """
# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.*.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        with open(target_service / "Dockerfile", 'w') as f:
            f.write(dockerfile_content)
        
        # 创建主requirements.txt
        all_requirements = set()
        for source_service in source_services:
            req_file = target_service / f"requirements.{source_service.name}.txt"
            if req_file.exists():
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            all_requirements.add(line)
        
        with open(target_service / "requirements.txt", 'w') as f:
            for req in sorted(all_requirements):
                f.write(f"{req}\n")
        
        # 创建README.md
        readme_content = f"""# {service_name.title().replace('-', ' ')}

这是一个合并后的微服务，包含以下原始服务：

"""
        for source_service in source_services:
            readme_content += f"- {source_service.name}\n"
        
        readme_content += f"""
## 架构说明

本服务通过合并多个相关微服务来简化架构，提高维护效率。

## 启动方式

```bash
docker build -t {service_name} .
docker run -p 8000:8000 {service_name}
```

## API文档

各子服务的API文档位于 `api/` 目录下。
"""
        
        with open(target_service / "README.md", 'w') as f:
            f.write(readme_content)
    
    def update_docker_compose(self):
        """更新docker-compose配置"""
        print("\n🔄 更新Docker Compose配置...")
        
        compose_file = self.project_root / "docker-compose.microservices.yml"
        if not compose_file.exists():
            print("❌ docker-compose.microservices.yml 不存在")
            return
        
        # 备份原文件
        backup_compose = self.project_root / "docker-compose.microservices.yml.backup"
        shutil.copy2(compose_file, backup_compose)
        print(f"  📦 备份配置文件: {backup_compose}")
        
        # 这里可以添加更新docker-compose的逻辑
        print("  ⚠️ 请手动更新docker-compose.microservices.yml文件")
    
    def cleanup_old_services(self, services_to_remove):
        """清理旧服务（可选）"""
        print(f"\n🗑️ 是否删除原始服务目录？")
        print("注意：已创建备份，但请确认合并成功后再删除")
        
        for service_name in services_to_remove:
            service_path = self.services_dir / service_name
            if service_path.exists():
                print(f"  - {service_name}")
        
        response = input("输入 'yes' 确认删除，其他任意键跳过: ")
        if response.lower() == 'yes':
            for service_name in services_to_remove:
                service_path = self.services_dir / service_name
                if service_path.exists():
                    shutil.rmtree(service_path)
                    print(f"  ✅ 删除: {service_name}")
        else:
            print("  ⏭️ 跳过删除，保留原始服务")
    
    def run_merge(self):
        """执行合并流程"""
        print("🚀 开始微服务合并流程...")
        
        # 加载分析结果
        analysis = self.load_analysis()
        if not analysis:
            return False
        
        print(f"📊 发现 {len(analysis['merge_recommendations'])} 个合并建议")
        
        success_count = 0
        
        # 执行合并
        for recommendation in analysis['merge_recommendations']:
            if recommendation['category'] == 'auth':
                if self.merge_auth_services():
                    success_count += 1
            elif recommendation['category'] == 'data':
                if self.merge_data_services():
                    success_count += 1
        
        # 更新配置
        self.update_docker_compose()
        
        print(f"\n✅ 合并完成! 成功合并 {success_count} 组服务")
        print(f"📦 备份位置: {self.backup_dir}")
        print("\n📋 下一步:")
        print("1. 检查合并后的服务代码")
        print("2. 更新docker-compose.microservices.yml")
        print("3. 测试合并后的服务")
        print("4. 确认无误后可删除原始服务")
        
        return True

def main():
    project_root = os.getcwd()
    merger = ServiceMerger(project_root)
    merger.run_merge()

if __name__ == "__main__":
    main() 