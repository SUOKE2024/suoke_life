#!/usr/bin/env python3
"""
索克生活无障碍服务 - 中期优化验证脚本

验证中期优化任务的完成情况，包括：
1. AI模型集成优化
2. 数据库连接池优化
3. API网关集成
4. 容器化部署配置
5. CI/CD流水线配置
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MidTermOptimizationValidator:
    """中期优化验证器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "warnings": 0,
            "details": {},
        }

    async def validate_all(self) -> Dict[str, Any]:
        """执行所有验证"""
        logger.info("🚀 开始中期优化验证...")

        validation_tasks = [
            ("AI模型集成优化", self.validate_ai_model_integration),
            ("数据库连接池优化", self.validate_database_pool_optimization),
            ("API网关集成", self.validate_api_gateway_integration),
            ("容器化部署配置", self.validate_containerization_config),
            ("CI/CD流水线配置", self.validate_cicd_pipeline),
        ]

        for task_name, task_func in validation_tasks:
            logger.info(f"📋 验证: {task_name}")
            try:
                result = await task_func()
                self.validation_results["details"][task_name] = result

                if result["status"] == "passed":
                    self.validation_results["passed_checks"] += result.get("checks", 1)
                elif result["status"] == "failed":
                    self.validation_results["failed_checks"] += result.get("checks", 1)
                elif result["status"] == "warning":
                    self.validation_results["warnings"] += result.get("checks", 1)

                self.validation_results["total_checks"] += result.get("checks", 1)

            except Exception as e:
                logger.error(f"❌ 验证失败: {task_name} - {e}")
                self.validation_results["details"][task_name] = {
                    "status": "failed",
                    "error": str(e),
                    "checks": 1,
                }
                self.validation_results["failed_checks"] += 1
                self.validation_results["total_checks"] += 1

        # 计算总体通过率
        total_checks = self.validation_results["total_checks"]
        passed_checks = self.validation_results["passed_checks"]
        self.validation_results["pass_rate"] = (
            (passed_checks / total_checks * 100) if total_checks > 0 else 0
        )

        return self.validation_results

    async def validate_ai_model_integration(self) -> Dict[str, Any]:
        """验证AI模型集成优化"""
        checks = []

        # 检查AI模型优化器文件
        ai_optimizer_file = self.project_root / "internal/service/ai_model_optimizer.py"
        if ai_optimizer_file.exists():
            checks.append({"name": "AI模型优化器文件存在", "status": "passed"})

            # 检查文件内容
            content = ai_optimizer_file.read_text()
            required_classes = [
                "ModelManager",
                "ModelCache",
                "BaseModelWrapper",
                "InferenceRequest",
                "InferenceResult",
            ]

            for class_name in required_classes:
                if f"class {class_name}" in content:
                    checks.append({"name": f"{class_name}类定义", "status": "passed"})
                else:
                    checks.append({"name": f"{class_name}类定义", "status": "failed"})
        else:
            checks.append({"name": "AI模型优化器文件存在", "status": "failed"})

        # 尝试导入模块
        try:
            from internal.service.ai_model_optimizer import (
                ModelConfig,
                ModelType,
                get_model_manager,
            )

            checks.append({"name": "AI模型优化器模块导入", "status": "passed"})

            # 测试基本功能
            config = {"cache_size": 100, "cache_ttl": 300, "max_workers": 2}
            manager = get_model_manager(config)
            checks.append({"name": "模型管理器实例化", "status": "passed"})

        except Exception as e:
            checks.append(
                {"name": "AI模型优化器模块导入", "status": "failed", "error": str(e)}
            )

        passed = sum(1 for check in checks if check["status"] == "passed")
        failed = sum(1 for check in checks if check["status"] == "failed")

        return {
            "status": "passed" if failed == 0 else "failed",
            "checks": len(checks),
            "passed": passed,
            "failed": failed,
            "details": checks,
        }

    async def validate_database_pool_optimization(self) -> Dict[str, Any]:
        """验证数据库连接池优化"""
        checks = []

        # 检查数据库连接池优化器文件
        db_optimizer_file = (
            self.project_root / "internal/service/database_pool_optimizer.py"
        )
        if db_optimizer_file.exists():
            checks.append({"name": "数据库连接池优化器文件存在", "status": "passed"})

            # 检查文件内容
            content = db_optimizer_file.read_text()
            required_classes = [
                "DatabasePoolManager",
                "ConnectionPool",
                "QueryOptimizer",
                "DatabaseConnection",
                "DatabaseConfig",
            ]

            for class_name in required_classes:
                if f"class {class_name}" in content:
                    checks.append({"name": f"{class_name}类定义", "status": "passed"})
                else:
                    checks.append({"name": f"{class_name}类定义", "status": "failed"})
        else:
            checks.append({"name": "数据库连接池优化器文件存在", "status": "failed"})

        # 尝试导入模块
        try:
            from internal.service.database_pool_optimizer import (
                DatabaseConfig,
                DatabaseType,
                get_database_manager,
            )

            checks.append({"name": "数据库连接池优化器模块导入", "status": "passed"})

            # 测试基本功能
            config = {"max_connections": 10}
            manager = get_database_manager(config)
            checks.append({"name": "数据库管理器实例化", "status": "passed"})

        except Exception as e:
            checks.append(
                {
                    "name": "数据库连接池优化器模块导入",
                    "status": "failed",
                    "error": str(e),
                }
            )

        passed = sum(1 for check in checks if check["status"] == "passed")
        failed = sum(1 for check in checks if check["status"] == "failed")

        return {
            "status": "passed" if failed == 0 else "failed",
            "checks": len(checks),
            "passed": passed,
            "failed": failed,
            "details": checks,
        }

    async def validate_api_gateway_integration(self) -> Dict[str, Any]:
        """验证API网关集成"""
        checks = []

        # 检查API网关文件
        api_gateway_file = self.project_root / "internal/service/api_gateway.py"
        if api_gateway_file.exists():
            checks.append({"name": "API网关文件存在", "status": "passed"})

            # 检查文件内容
            content = api_gateway_file.read_text()
            required_classes = [
                "APIGateway",
                "Router",
                "AuthenticationManager",
                "RateLimiter",
                "ResponseCache",
            ]

            for class_name in required_classes:
                if f"class {class_name}" in content:
                    checks.append({"name": f"{class_name}类定义", "status": "passed"})
                else:
                    checks.append({"name": f"{class_name}类定义", "status": "failed"})
        else:
            checks.append({"name": "API网关文件存在", "status": "failed"})

        # 尝试导入模块
        try:
            from internal.service.api_gateway import (
                APIRequest,
                APIResponse,
                get_api_gateway,
            )

            checks.append({"name": "API网关模块导入", "status": "passed"})

            # 测试基本功能
            config = {
                "auth": {"jwt_secret": "test_secret"},
                "rate_limit": {"enabled": False},
            }
            gateway = get_api_gateway(config)
            checks.append({"name": "API网关实例化", "status": "passed"})

        except Exception as e:
            checks.append(
                {"name": "API网关模块导入", "status": "failed", "error": str(e)}
            )

        passed = sum(1 for check in checks if check["status"] == "passed")
        failed = sum(1 for check in checks if check["status"] == "failed")

        return {
            "status": "passed" if failed == 0 else "failed",
            "checks": len(checks),
            "passed": passed,
            "failed": failed,
            "details": checks,
        }

    async def validate_containerization_config(self) -> Dict[str, Any]:
        """验证容器化部署配置"""
        checks = []

        # 检查Dockerfile
        dockerfile = self.project_root / "Dockerfile"
        if dockerfile.exists():
            checks.append({"name": "Dockerfile存在", "status": "passed"})

            content = dockerfile.read_text()
            required_elements = [
                "FROM python:3.11-slim",
                "WORKDIR /app",
                "COPY requirements.txt",
                "RUN pip install",
                "EXPOSE 8080",
                "CMD",
            ]

            for element in required_elements:
                if element in content:
                    checks.append(
                        {"name": f"Dockerfile包含{element}", "status": "passed"}
                    )
                else:
                    checks.append(
                        {"name": f"Dockerfile包含{element}", "status": "failed"}
                    )
        else:
            checks.append({"name": "Dockerfile存在", "status": "failed"})

        # 检查docker-compose.yml
        docker_compose = self.project_root / "docker-compose.yml"
        if docker_compose.exists():
            checks.append({"name": "docker-compose.yml存在", "status": "passed"})

            content = docker_compose.read_text()
            required_services = [
                "accessibility-service",
                "postgres",
                "redis",
                "nginx",
                "prometheus",
                "grafana",
            ]

            for service in required_services:
                if f"{service}:" in content:
                    checks.append(
                        {"name": f"docker-compose包含{service}服务", "status": "passed"}
                    )
                else:
                    checks.append(
                        {"name": f"docker-compose包含{service}服务", "status": "failed"}
                    )
        else:
            checks.append({"name": "docker-compose.yml存在", "status": "failed"})

        passed = sum(1 for check in checks if check["status"] == "passed")
        failed = sum(1 for check in checks if check["status"] == "failed")

        return {
            "status": "passed" if failed == 0 else "failed",
            "checks": len(checks),
            "passed": passed,
            "failed": failed,
            "details": checks,
        }

    async def validate_cicd_pipeline(self) -> Dict[str, Any]:
        """验证CI/CD流水线配置"""
        checks = []

        # 检查GitHub Actions配置
        github_workflow = self.project_root / ".github/workflows/ci-cd.yml"
        if github_workflow.exists():
            checks.append({"name": "GitHub Actions工作流文件存在", "status": "passed"})

            content = github_workflow.read_text()
            required_jobs = [
                "code-quality",
                "unit-tests",
                "integration-tests",
                "build-image",
                "security-scan",
                "deploy-dev",
                "deploy-prod",
            ]

            for job in required_jobs:
                if f"{job}:" in content:
                    checks.append({"name": f"CI/CD包含{job}任务", "status": "passed"})
                else:
                    checks.append({"name": f"CI/CD包含{job}任务", "status": "failed"})
        else:
            checks.append({"name": "GitHub Actions工作流文件存在", "status": "failed"})

        passed = sum(1 for check in checks if check["status"] == "passed")
        failed = sum(1 for check in checks if check["status"] == "failed")

        return {
            "status": "passed" if failed == 0 else "failed",
            "checks": len(checks),
            "passed": passed,
            "failed": failed,
            "details": checks,
        }

    def generate_report(self) -> str:
        """生成验证报告"""
        results = self.validation_results

        report = f"""
🎯 索克生活无障碍服务 - 中期优化验证报告
{'='*60}

📊 总体统计:
- 验证时间: {results['timestamp']}
- 总检查项: {results['total_checks']}
- 通过检查: {results['passed_checks']}
- 失败检查: {results['failed_checks']}
- 警告检查: {results['warnings']}
- 通过率: {results['pass_rate']:.1f}%

📋 详细结果:
"""

        for task_name, task_result in results["details"].items():
            status_emoji = (
                "✅"
                if task_result["status"] == "passed"
                else "❌" if task_result["status"] == "failed" else "⚠️"
            )
            report += f"\n{status_emoji} {task_name}:\n"
            report += f"   状态: {task_result['status']}\n"
            report += f"   检查项: {task_result.get('checks', 0)}\n"
            report += f"   通过: {task_result.get('passed', 0)}\n"
            report += f"   失败: {task_result.get('failed', 0)}\n"

            if "error" in task_result:
                report += f"   错误: {task_result['error']}\n"

            if "details" in task_result:
                for detail in task_result["details"]:
                    detail_emoji = "✅" if detail["status"] == "passed" else "❌"
                    report += f"     {detail_emoji} {detail['name']}\n"
                    if "error" in detail:
                        report += f"        错误: {detail['error']}\n"

        # 添加建议
        report += f"\n💡 优化建议:\n"

        if results["failed_checks"] > 0:
            report += "- 请修复失败的检查项以确保系统稳定性\n"

        if results["pass_rate"] < 90:
            report += "- 通过率较低，建议优先处理关键问题\n"
        elif results["pass_rate"] >= 95:
            report += "- 系统状态良好，可以继续进行长期优化\n"

        report += "- 定期运行验证脚本以监控系统状态\n"
        report += "- 关注性能指标和用户反馈\n"

        return report


async def main():
    """主函数"""
    start_time = time.time()

    validator = MidTermOptimizationValidator()

    try:
        # 执行验证
        results = await validator.validate_all()

        # 生成报告
        report = validator.generate_report()
        print(report)

        # 保存结果到文件
        results_file = validator.project_root / "validation_results_mid_term.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        report_file = validator.project_root / "validation_report_mid_term.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        execution_time = time.time() - start_time

        print(f"\n⏱️  验证完成，耗时: {execution_time:.2f}秒")
        print(f"📄 详细结果已保存到: {results_file}")
        print(f"📄 验证报告已保存到: {report_file}")

        # 根据结果设置退出码
        if results["failed_checks"] > 0:
            print(f"\n❌ 验证失败: {results['failed_checks']} 个检查项未通过")
            sys.exit(1)
        elif results["warnings"] > 0:
            print(f"\n⚠️  验证完成但有警告: {results['warnings']} 个检查项需要注意")
            sys.exit(0)
        else:
            print(f"\n✅ 验证成功: 所有检查项均通过")
            sys.exit(0)

    except Exception as e:
        logger.error(f"验证过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
