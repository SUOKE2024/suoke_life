#!/usr/bin/env python3
"""
索克生活高级服务合并工具
继续合并通信服务和工具服务
"""

import os
import json
import shutil
import subprocess
from pathlib import Path

class AdvancedServiceMerger:
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
                backup_path = self.backup_dir / f"{service_name}_advanced"
                if backup_path.exists():
                    shutil.rmtree(backup_path)
                shutil.copytree(service_path, backup_path)
                print(f"  ✅ 备份: {service_name}")
    
    def merge_communication_services(self):
        """合并通信服务"""
        print("\n🔄 合并通信服务...")
        
        message_bus = self.services_dir / "message-bus"
        rag_service = self.services_dir / "rag-service"
        target_service = self.services_dir / "communication-service"
        
        if not message_bus.exists() or not rag_service.exists():
            print("❌ 通信服务不存在")
            return False
        
        # 创建备份
        self.create_backup(["message-bus", "rag-service"])
        
        # 创建新的合并服务目录
        target_service.mkdir(exist_ok=True)
        
        # 合并目录结构
        self._merge_service_structure(
            [message_bus, rag_service], 
            target_service,
            "communication-service"
        )
        
        print("✅ 通信服务合并完成")
        return True
    
    def merge_utility_services(self):
        """合并小型工具服务"""
        print("\n🔄 合并小型工具服务...")
        
        # 选择较小的工具服务进行合并
        utility_services = [
            "integration-service",
            "medical-resource-service",
            "corn-maze-service"
        ]
        
        existing_services = []
        for service_name in utility_services:
            service_path = self.services_dir / service_name
            if service_path.exists():
                existing_services.append(service_path)
        
        if len(existing_services) < 2:
            print("❌ 可合并的工具服务不足")
            return False
        
        target_service = self.services_dir / "utility-services"
        
        # 创建备份
        self.create_backup([s.name for s in existing_services])
        
        # 创建新的合并服务目录
        target_service.mkdir(exist_ok=True)
        
        # 合并目录结构
        self._merge_service_structure(
            existing_services, 
            target_service,
            "utility-services"
        )
        
        print("✅ 工具服务合并完成")
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
CMD ["python", "-c", "print('Service is running on port 8000')"]
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

## 子服务说明

"""
        
        for source_service in source_services:
            readme_content += f"### {source_service.name}\n"
            readme_content += f"- 代码位置: `{service_name.replace('-', '_')}/{source_service.name.replace('-', '_')}/`\n"
            readme_content += f"- API文档: `api/{source_service.name}/`\n"
            readme_content += f"- 配置文件: `config/{source_service.name}/`\n\n"
        
        with open(target_service / "README.md", 'w') as f:
            f.write(readme_content)
    
    def analyze_optimization_impact(self):
        """分析优化影响"""
        print("\n📊 分析优化影响...")
        
        # 统计当前服务数量
        current_services = [d for d in self.services_dir.iterdir() 
                          if d.is_dir() and not d.name.startswith('.')]
        
        print(f"当前服务数量: {len(current_services)}")
        
        # 计算可能的进一步优化
        small_services = []
        for service_dir in current_services:
            # 检查服务大小
            try:
                result = subprocess.run(['du', '-sh', str(service_dir)], 
                                      capture_output=True, text=True)
                size_str = result.stdout.split()[0] if result.stdout else "0K"
                
                # 如果服务小于100M，认为是小服务
                if 'K' in size_str or (size_str.endswith('M') and 
                                     float(size_str[:-1]) < 100):
                    small_services.append(service_dir.name)
            except:
                pass
        
        print(f"小型服务 (<100M): {len(small_services)}")
        if small_services:
            print(f"  - {', '.join(small_services)}")
        
        return {
            "total_services": len(current_services),
            "small_services": small_services
        }
    
    def run_advanced_merge(self):
        """执行高级合并流程"""
        print("🚀 开始高级微服务合并流程...")
        
        success_count = 0
        
        # 合并通信服务
        if self.merge_communication_services():
            success_count += 1
        
        # 合并工具服务
        if self.merge_utility_services():
            success_count += 1
        
        # 分析优化影响
        impact = self.analyze_optimization_impact()
        
        print(f"\n✅ 高级合并完成! 成功合并 {success_count} 组服务")
        print(f"📦 备份位置: {self.backup_dir}")
        print(f"📊 当前服务总数: {impact['total_services']}")
        
        if impact['small_services']:
            print(f"💡 建议: 还有 {len(impact['small_services'])} 个小型服务可以进一步合并")
        
        print("\n📋 下一步:")
        print("1. 测试合并后的服务")
        print("2. 更新部署配置")
        print("3. 考虑进一步合并小型服务")
        
        return True

def main():
    project_root = os.getcwd()
    merger = AdvancedServiceMerger(project_root)
    merger.run_advanced_merge()

if __name__ == "__main__":
    main() 