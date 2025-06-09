#!/usr/bin/env python3
"""
索克生活部署配置更新工具
更新Docker Compose和Kubernetes配置以反映服务合并
"""

import os
import yaml
import json
from pathlib import Path
import shutil

class DeploymentConfigUpdater:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.docker_compose_file = self.project_root / "docker-compose.microservices.yml"
        self.backup_dir = self.project_root / "backup" / "deployment"
        
        # 服务合并映射
        self.service_merges = {
            # 原始服务 -> 合并后的服务
            "auth-service": "user-management-service",
            "user-service": "user-management-service",
            "health-data-service": "unified-health-data-service",
            "database": "unified-health-data-service",
            "message-bus": "communication-service",
            "rag-service": "communication-service",
            "integration-service": "utility-services",
            "medical-resource-service": "utility-services",
            "corn-maze-service": "utility-services"
        }
        
        # 新服务端口映射
        self.new_service_ports = {
            "user-management-service": "8001:8000",
            "unified-health-data-service": "8002:8000", 
            "communication-service": "8030:8000",
            "utility-services": "8040:8000"
        }
    
    def create_backup(self):
        """创建配置文件备份"""
        print("📦 创建部署配置备份...")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        if self.docker_compose_file.exists():
            backup_file = self.backup_dir / f"docker-compose.microservices.yml.{os.popen('date +%Y%m%d_%H%M%S').read().strip()}"
            shutil.copy2(self.docker_compose_file, backup_file)
            print(f"  ✅ 备份Docker Compose: {backup_file}")
        
        # 备份k8s配置
        k8s_dir = self.project_root / "k8s"
        if k8s_dir.exists():
            k8s_backup = self.backup_dir / "k8s"
            if k8s_backup.exists():
                shutil.rmtree(k8s_backup)
            shutil.copytree(k8s_dir, k8s_backup)
            print(f"  ✅ 备份Kubernetes配置: {k8s_backup}")
    
    def load_docker_compose(self):
        """加载Docker Compose配置"""
        if not self.docker_compose_file.exists():
            print(f"❌ Docker Compose文件不存在: {self.docker_compose_file}")
            return None
        
        with open(self.docker_compose_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def update_docker_compose(self):
        """更新Docker Compose配置"""
        print("\n🔄 更新Docker Compose配置...")
        
        config = self.load_docker_compose()
        if not config:
            return False
        
        services = config.get('services', {})
        updated_services = {}
        removed_services = []
        added_services = []
        
        # 处理现有服务
        for service_name, service_config in services.items():
            if service_name in self.service_merges:
                # 这个服务已被合并，跳过
                removed_services.append(service_name)
                print(f"  🗑️ 移除已合并服务: {service_name}")
                continue
            else:
                # 保留未合并的服务
                updated_services[service_name] = service_config
        
        # 添加新的合并服务
        for merged_service in set(self.service_merges.values()):
            if merged_service not in updated_services:
                service_config = self._create_merged_service_config(merged_service)
                updated_services[merged_service] = service_config
                added_services.append(merged_service)
                print(f"  ➕ 添加合并服务: {merged_service}")
        
        # 更新依赖关系
        self._update_service_dependencies(updated_services)
        
        # 更新配置
        config['services'] = updated_services
        
        # 保存更新后的配置
        with open(self.docker_compose_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"  ✅ Docker Compose配置已更新")
        print(f"  📊 移除服务: {len(removed_services)}个")
        print(f"  📊 添加服务: {len(added_services)}个")
        
        return True
    
    def _create_merged_service_config(self, service_name):
        """创建合并服务的配置"""
        base_config = {
            "build": f"./services/{service_name}",
            "depends_on": ["postgres", "redis"],
            "environment": {
                "API_PORT": "8000",
                "DATABASE_URL": "postgresql://suoke:suoke123@postgres:5432/suoke_db",
                "REDIS_URL": "redis://redis:6379/0",
                "SERVICE_NAME": service_name
            },
            "networks": ["suoke-network"],
            "ports": [self.new_service_ports.get(service_name, "8000:8000")],
            "restart": "unless-stopped",
            "volumes": ["logs_data:/app/logs"]
        }
        
        # 根据服务类型添加特定依赖
        if service_name == "user-management-service":
            # 用户管理服务可能需要区块链服务
            base_config["depends_on"].append("blockchain-service")
        elif service_name == "communication-service":
            # 通信服务可能需要用户管理服务
            base_config["depends_on"].append("user-management-service")
        elif service_name == "utility-services":
            # 工具服务可能需要用户管理和通信服务
            base_config["depends_on"].extend(["user-management-service", "communication-service"])
        
        return base_config
    
    def _update_service_dependencies(self, services):
        """更新服务依赖关系"""
        print("  🔗 更新服务依赖关系...")
        
        for service_name, service_config in services.items():
            depends_on = service_config.get('depends_on', [])
            updated_depends = []
            
            for dep in depends_on:
                if dep in self.service_merges:
                    # 依赖已被合并，更新为新服务
                    new_dep = self.service_merges[dep]
                    if new_dep not in updated_depends and new_dep != service_name:
                        updated_depends.append(new_dep)
                else:
                    # 保留原有依赖
                    if dep not in updated_depends:
                        updated_depends.append(dep)
            
            service_config['depends_on'] = updated_depends
    
    def update_kubernetes_config(self):
        """更新Kubernetes配置"""
        print("\n🔄 更新Kubernetes配置...")
        
        k8s_dir = self.project_root / "k8s"
        if not k8s_dir.exists():
            print("  ⚠️ Kubernetes目录不存在，跳过")
            return True
        
        # 创建新的部署文件
        self._create_k8s_deployments()
        
        print("  ✅ Kubernetes配置已更新")
        return True
    
    def _create_k8s_deployments(self):
        """创建Kubernetes部署文件"""
        k8s_dir = self.project_root / "k8s"
        
        for service_name in set(self.service_merges.values()):
            deployment_file = k8s_dir / f"{service_name}-deployment.yaml"
            
            deployment_config = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": service_name,
                    "labels": {
                        "app": service_name
                    }
                },
                "spec": {
                    "replicas": 2,
                    "selector": {
                        "matchLabels": {
                            "app": service_name
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": service_name
                            }
                        },
                        "spec": {
                            "containers": [{
                                "name": service_name,
                                "image": f"suoke/{service_name}:latest",
                                "ports": [{
                                    "containerPort": 8000
                                }],
                                "env": [
                                    {"name": "API_PORT", "value": "8000"},
                                    {"name": "DATABASE_URL", "value": "postgresql://suoke:suoke123@postgres:5432/suoke_db"},
                                    {"name": "REDIS_URL", "value": "redis://redis:6379/0"},
                                    {"name": "SERVICE_NAME", "value": service_name}
                                ]
                            }]
                        }
                    }
                }
            }
            
            with open(deployment_file, 'w', encoding='utf-8') as f:
                yaml.dump(deployment_config, f, default_flow_style=False, allow_unicode=True)
            
            print(f"    📄 创建K8s部署: {deployment_file}")
    
    def generate_update_report(self):
        """生成更新报告"""
        report = []
        report.append("# 部署配置更新报告\n")
        report.append(f"**更新时间**: {os.popen('date').read().strip()}\n")
        
        report.append("## 服务合并映射\n")
        for old_service, new_service in self.service_merges.items():
            report.append(f"- `{old_service}` → `{new_service}`")
        report.append("")
        
        report.append("## 新服务端口映射\n")
        for service, port in self.new_service_ports.items():
            report.append(f"- `{service}`: {port}")
        report.append("")
        
        report.append("## 更新内容\n")
        report.append("### Docker Compose")
        report.append("- ✅ 移除已合并的原始服务")
        report.append("- ✅ 添加新的合并服务")
        report.append("- ✅ 更新服务依赖关系")
        report.append("- ✅ 配置新的端口映射")
        report.append("")
        
        report.append("### Kubernetes")
        report.append("- ✅ 创建新服务的Deployment文件")
        report.append("- ✅ 配置环境变量和资源")
        report.append("")
        
        report.append("## 验证步骤\n")
        report.append("```bash")
        report.append("# 验证Docker Compose配置")
        report.append("docker-compose -f docker-compose.microservices.yml config")
        report.append("")
        report.append("# 启动更新后的服务")
        report.append("docker-compose -f docker-compose.microservices.yml up -d")
        report.append("")
        report.append("# 验证Kubernetes配置")
        report.append("kubectl apply --dry-run=client -f k8s/")
        report.append("```")
        
        return "\n".join(report)
    
    def run_update(self):
        """执行配置更新"""
        print("🚀 开始更新部署配置...")
        
        # 创建备份
        self.create_backup()
        
        # 更新Docker Compose
        if not self.update_docker_compose():
            print("❌ Docker Compose更新失败")
            return False
        
        # 更新Kubernetes配置
        if not self.update_kubernetes_config():
            print("❌ Kubernetes配置更新失败")
            return False
        
        # 生成报告
        report_content = self.generate_update_report()
        report_path = self.project_root / "DEPLOYMENT_CONFIG_UPDATE_REPORT.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n✅ 部署配置更新完成!")
        print(f"📄 更新报告: {report_path}")
        print(f"📦 备份位置: {self.backup_dir}")
        
        print(f"\n📋 下一步:")
        print("1. 验证配置: docker-compose -f docker-compose.microservices.yml config")
        print("2. 测试启动: docker-compose -f docker-compose.microservices.yml up -d")
        print("3. 检查服务状态: docker-compose ps")
        
        return True

def main():
    project_root = os.getcwd()
    updater = DeploymentConfigUpdater(project_root)
    updater.run_update()

if __name__ == "__main__":
    main() 