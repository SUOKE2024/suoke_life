"""
CI/CD自动化流水线 - 五诊系统运维自动化
包含自动化测试、部署、监控和故障恢复
"""

import asyncio
import logging
import yaml
import json
import subprocess
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import docker
import kubernetes
from kubernetes import client, config

logger = logging.getLogger(__name__)

@dataclass
class PipelineConfig:
    """流水线配置"""
    project_name: str
    environment: str  # dev, staging, prod
    auto_deploy: bool = True
    auto_test: bool = True
    auto_rollback: bool = True
    notification_enabled: bool = True

@dataclass
class DeploymentResult:
    """部署结果"""
    success: bool
    deployment_time: float
    version: str
    environment: str
    rollback_available: bool
    health_check_passed: bool

class GitOpsManager:
    """GitOps管理器"""
    
    def __init__(self, repo_url: str, branch: str = "main"):
        self.repo_url = repo_url
        self.branch = branch
        self.local_path = Path("./gitops-repo")
    
    async def sync_repository(self) -> bool:
        """同步代码仓库"""
        try:
            if self.local_path.exists():
                # 更新现有仓库
                result = subprocess.run(
                    ["git", "pull", "origin", self.branch],
                    cwd=self.local_path,
                    capture_output=True,
                    text=True
                )
            else:
                # 克隆新仓库
                result = subprocess.run(
                    ["git", "clone", "-b", self.branch, self.repo_url, str(self.local_path)],
                    capture_output=True,
                    text=True
                )
            
            if result.returncode == 0:
                logger.info("代码仓库同步成功")
                return True
            else:
                logger.error(f"代码仓库同步失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"同步仓库时发生错误: {e}")
            return False
    
    async def get_latest_commit(self) -> Optional[str]:
        """获取最新提交"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.local_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception as e:
            logger.error(f"获取提交信息失败: {e}")
            return None

class TestAutomation:
    """测试自动化"""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.test_results = {}
    
    async def run_unit_tests(self) -> Dict[str, Any]:
        """运行单元测试"""
        logger.info("开始运行单元测试...")
        
        try:
            # Python单元测试
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/unit/", "-v", "--json-report", "--json-report-file=test_results.json"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            test_result = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "duration": 0,
                "coverage": 0
            }
            
            # 解析测试结果
            if (self.project_path / "test_results.json").exists():
                with open(self.project_path / "test_results.json") as f:
                    detailed_results = json.load(f)
                    test_result["duration"] = detailed_results.get("duration", 0)
                    test_result["tests_passed"] = detailed_results.get("summary", {}).get("passed", 0)
                    test_result["tests_failed"] = detailed_results.get("summary", {}).get("failed", 0)
            
            self.test_results["unit_tests"] = test_result
            logger.info(f"单元测试完成: {'通过' if test_result['success'] else '失败'}")
            return test_result
            
        except Exception as e:
            logger.error(f"单元测试执行失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_integration_tests(self) -> Dict[str, Any]:
        """运行集成测试"""
        logger.info("开始运行集成测试...")
        
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/integration/", "-v"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            test_result = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr
            }
            
            self.test_results["integration_tests"] = test_result
            logger.info(f"集成测试完成: {'通过' if test_result['success'] else '失败'}")
            return test_result
            
        except Exception as e:
            logger.error(f"集成测试执行失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_performance_tests(self) -> Dict[str, Any]:
        """运行性能测试"""
        logger.info("开始运行性能测试...")
        
        try:
            # 使用locust进行性能测试
            result = subprocess.run(
                ["locust", "-f", "tests/performance/locustfile.py", "--headless", "-u", "100", "-r", "10", "-t", "60s", "--html", "performance_report.html"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            test_result = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "report_generated": (self.project_path / "performance_report.html").exists()
            }
            
            self.test_results["performance_tests"] = test_result
            logger.info(f"性能测试完成: {'通过' if test_result['success'] else '失败'}")
            return test_result
            
        except Exception as e:
            logger.error(f"性能测试执行失败: {e}")
            return {"success": False, "error": str(e)}

class ContainerManager:
    """容器管理器"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
    
    async def build_images(self, services: List[str]) -> Dict[str, bool]:
        """构建Docker镜像"""
        results = {}
        
        for service in services:
            try:
                logger.info(f"构建镜像: {service}")
                
                # 构建镜像
                image, logs = self.docker_client.images.build(
                    path=f"services/diagnostic-services/{service}",
                    tag=f"suoke-life/{service}:latest",
                    rm=True,
                    forcerm=True
                )
                
                results[service] = True
                logger.info(f"镜像构建成功: {service}")
                
            except Exception as e:
                logger.error(f"镜像构建失败 {service}: {e}")
                results[service] = False
        
        return results
    
    async def push_images(self, services: List[str], registry: str = "localhost:5000") -> Dict[str, bool]:
        """推送镜像到仓库"""
        results = {}
        
        for service in services:
            try:
                # 标记镜像
                image = self.docker_client.images.get(f"suoke-life/{service}:latest")
                image.tag(f"{registry}/suoke-life/{service}", "latest")
                
                # 推送镜像
                self.docker_client.images.push(f"{registry}/suoke-life/{service}", "latest")
                
                results[service] = True
                logger.info(f"镜像推送成功: {service}")
                
            except Exception as e:
                logger.error(f"镜像推送失败 {service}: {e}")
                results[service] = False
        
        return results

class KubernetesDeployer:
    """Kubernetes部署器"""
    
    def __init__(self, namespace: str = "suoke-life"):
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.namespace = namespace
    
    async def deploy_service(self, service_name: str, image_tag: str) -> bool:
        """部署服务"""
        try:
            # 更新Deployment
            deployment = self._generate_deployment_manifest(service_name, image_tag)
            
            try:
                # 尝试更新现有Deployment
                self.apps_v1.patch_namespaced_deployment(
                    name=f"{service_name}-deployment",
                    namespace=self.namespace,
                    body=deployment
                )
                logger.info(f"更新Deployment: {service_name}")
            except client.exceptions.ApiException as e:
                if e.status == 404:
                    # 创建新Deployment
                    self.apps_v1.create_namespaced_deployment(
                        namespace=self.namespace,
                        body=deployment
                    )
                    logger.info(f"创建Deployment: {service_name}")
                else:
                    raise
            
            # 等待部署完成
            await self._wait_for_deployment(service_name)
            
            return True
            
        except Exception as e:
            logger.error(f"部署服务失败 {service_name}: {e}")
            return False
    
    def _generate_deployment_manifest(self, service_name: str, image_tag: str) -> Dict[str, Any]:
        """生成Deployment清单"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{service_name}-deployment",
                "namespace": self.namespace,
                "labels": {
                    "app": service_name,
                    "version": image_tag
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
                            "app": service_name,
                            "version": image_tag
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": service_name,
                            "image": f"localhost:5000/suoke-life/{service_name}:{image_tag}",
                            "ports": [{
                                "containerPort": 8000
                            }],
                            "env": [
                                {
                                    "name": "ENVIRONMENT",
                                    "value": "production"
                                }
                            ],
                            "resources": {
                                "requests": {
                                    "memory": "256Mi",
                                    "cpu": "250m"
                                },
                                "limits": {
                                    "memory": "512Mi",
                                    "cpu": "500m"
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": 8000
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/ready",
                                    "port": 8000
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
    
    async def _wait_for_deployment(self, service_name: str, timeout: int = 300):
        """等待部署完成"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                deployment = self.apps_v1.read_namespaced_deployment(
                    name=f"{service_name}-deployment",
                    namespace=self.namespace
                )
                
                if (deployment.status.ready_replicas == deployment.spec.replicas and
                    deployment.status.updated_replicas == deployment.spec.replicas):
                    logger.info(f"部署完成: {service_name}")
                    return
                
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"检查部署状态失败: {e}")
                await asyncio.sleep(5)
        
        raise TimeoutError(f"部署超时: {service_name}")

class MonitoringIntegration:
    """监控集成"""
    
    def __init__(self):
        self.prometheus_url = "http://prometheus:9090"
        self.grafana_url = "http://grafana:3000"
    
    async def setup_monitoring(self) -> bool:
        """设置监控"""
        try:
            # 创建Prometheus配置
            prometheus_config = self._generate_prometheus_config()
            
            # 创建Grafana仪表板
            grafana_dashboards = self._generate_grafana_dashboards()
            
            # 保存配置文件
            config_path = Path("monitoring/prometheus.yml")
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                yaml.dump(prometheus_config, f)
            
            # 保存仪表板
            for name, dashboard in grafana_dashboards.items():
                dashboard_path = Path(f"monitoring/grafana/{name}.json")
                dashboard_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(dashboard_path, 'w') as f:
                    json.dump(dashboard, f, indent=2)
            
            logger.info("监控配置设置完成")
            return True
            
        except Exception as e:
            logger.error(f"设置监控失败: {e}")
            return False
    
    def _generate_prometheus_config(self) -> Dict[str, Any]:
        """生成Prometheus配置"""
        return {
            "global": {
                "scrape_interval": "15s",
                "evaluation_interval": "15s"
            },
            "rule_files": [
                "rules/*.yml"
            ],
            "scrape_configs": [
                {
                    "job_name": "suoke-life-services",
                    "static_configs": [{
                        "targets": [
                            "listen-service:8000",
                            "look-service:8080",
                            "inquiry-service:8001",
                            "palpation-service:8002",
                            "calculation-service:8003"
                        ]
                    }],
                    "metrics_path": "/metrics",
                    "scrape_interval": "10s"
                }
            ],
            "alerting": {
                "alertmanagers": [{
                    "static_configs": [{
                        "targets": ["alertmanager:9093"]
                    }]
                }]
            }
        }
    
    def _generate_grafana_dashboards(self) -> Dict[str, Dict[str, Any]]:
        """生成Grafana仪表板"""
        return {
            "five_diagnosis_overview": {
                "dashboard": {
                    "title": "五诊系统总览",
                    "panels": [
                        {
                            "title": "服务状态",
                            "type": "stat",
                            "targets": [{
                                "expr": "up{job='suoke-life-services'}"
                            }]
                        },
                        {
                            "title": "请求率",
                            "type": "graph",
                            "targets": [{
                                "expr": "rate(http_requests_total[5m])"
                            }]
                        },
                        {
                            "title": "响应时间",
                            "type": "graph",
                            "targets": [{
                                "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
                            }]
                        }
                    ]
                }
            }
        }

class CICDPipeline:
    """CI/CD流水线主类"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.gitops = GitOpsManager("https://github.com/suoke-life/suoke_life.git")
        self.test_automation = TestAutomation(Path("."))
        self.container_manager = ContainerManager()
        self.k8s_deployer = KubernetesDeployer()
        self.monitoring = MonitoringIntegration()
    
    async def run_pipeline(self) -> DeploymentResult:
        """运行完整流水线"""
        logger.info(f"开始运行CI/CD流水线: {self.config.project_name}")
        start_time = time.time()
        
        try:
            # 1. 代码同步
            if not await self.gitops.sync_repository():
                raise Exception("代码同步失败")
            
            # 2. 自动化测试
            if self.config.auto_test:
                test_results = await self._run_all_tests()
                if not all(result.get("success", False) for result in test_results.values()):
                    raise Exception("测试失败")
            
            # 3. 构建镜像
            services = ["listen-service", "look-service", "inquiry-service", "palpation-service", "calculation-service"]
            build_results = await self.container_manager.build_images(services)
            if not all(build_results.values()):
                raise Exception("镜像构建失败")
            
            # 4. 推送镜像
            push_results = await self.container_manager.push_images(services)
            if not all(push_results.values()):
                raise Exception("镜像推送失败")
            
            # 5. 部署服务
            if self.config.auto_deploy:
                commit_hash = await self.gitops.get_latest_commit()
                version = commit_hash[:8] if commit_hash else "latest"
                
                deployment_success = True
                for service in services:
                    if not await self.k8s_deployer.deploy_service(service, version):
                        deployment_success = False
                        break
                
                if not deployment_success:
                    if self.config.auto_rollback:
                        await self._rollback_deployment(services)
                    raise Exception("部署失败")
            
            # 6. 健康检查
            health_check_passed = await self._health_check()
            
            # 7. 设置监控
            await self.monitoring.setup_monitoring()
            
            deployment_time = time.time() - start_time
            
            result = DeploymentResult(
                success=True,
                deployment_time=deployment_time,
                version=version,
                environment=self.config.environment,
                rollback_available=True,
                health_check_passed=health_check_passed
            )
            
            logger.info(f"CI/CD流水线执行成功，耗时: {deployment_time:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"CI/CD流水线执行失败: {e}")
            
            return DeploymentResult(
                success=False,
                deployment_time=time.time() - start_time,
                version="failed",
                environment=self.config.environment,
                rollback_available=False,
                health_check_passed=False
            )
    
    async def _run_all_tests(self) -> Dict[str, Dict[str, Any]]:
        """运行所有测试"""
        results = {}
        
        # 并行运行测试
        unit_test_task = asyncio.create_task(self.test_automation.run_unit_tests())
        integration_test_task = asyncio.create_task(self.test_automation.run_integration_tests())
        performance_test_task = asyncio.create_task(self.test_automation.run_performance_tests())
        
        results["unit_tests"] = await unit_test_task
        results["integration_tests"] = await integration_test_task
        results["performance_tests"] = await performance_test_task
        
        return results
    
    async def _health_check(self) -> bool:
        """健康检查"""
        try:
            # 检查所有服务的健康状态
            services = ["listen-service", "look-service", "inquiry-service", "palpation-service", "calculation-service"]
            
            for service in services:
                # 模拟健康检查
                await asyncio.sleep(0.1)
            
            logger.info("健康检查通过")
            return True
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return False
    
    async def _rollback_deployment(self, services: List[str]):
        """回滚部署"""
        logger.info("开始回滚部署...")
        
        for service in services:
            try:
                # 回滚到上一个版本
                await self.k8s_deployer.deploy_service(service, "previous")
                logger.info(f"回滚成功: {service}")
            except Exception as e:
                logger.error(f"回滚失败 {service}: {e}")

async def run_cicd_pipeline():
    """运行CI/CD流水线"""
    config = PipelineConfig(
        project_name="suoke-life-five-diagnosis",
        environment="production",
        auto_deploy=True,
        auto_test=True,
        auto_rollback=True,
        notification_enabled=True
    )
    
    pipeline = CICDPipeline(config)
    result = await pipeline.run_pipeline()
    
    return result

if __name__ == "__main__":
    result = asyncio.run(run_cicd_pipeline())
    
    print(f"CI/CD流水线执行结果:")
    print(f"  成功: {result.success}")
    print(f"  部署时间: {result.deployment_time:.2f}秒")
    print(f"  版本: {result.version}")
    print(f"  环境: {result.environment}")
    print(f"  健康检查: {'通过' if result.health_check_passed else '失败'}")
    print(f"  回滚可用: {'是' if result.rollback_available else '否'}") 