"""
fix_dependencies - 索克生活项目模块
"""

from pathlib import Path
from typing import Dict, List, Tuple
import re

#!/usr/bin/env python3
"""
索克生活项目 - 依赖冲突修复脚本
修复uv迁移过程中的版本冲突问题
"""


class DependencyFixer:
    """依赖冲突修复器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.services_dir = self.project_root / "services"

        # 统一版本映射
        self.version_map = {
            "email-validator": ">=2.1.0",
            "prometheus-client": ">=0.19.0", 
            "opentelemetry-api": ">=1.21.0",
            "opentelemetry-sdk": ">=1.21.0",
            "opentelemetry-exporter-otlp": ">=1.21.0",
            "opentelemetry-instrumentation-fastapi": ">=0.42b0",
            "opentelemetry-instrumentation-redis": ">=0.42b0",
            "opentelemetry-instrumentation-sqlalchemy": ">=0.42b0",
            "opentelemetry-instrumentation-aiohttp-client": ">=0.42b0",
            "opentelemetry-semantic-conventions": ">=0.42b0",
            # 智能体服务特殊依赖
            "pyjwt": ">=2.8.0,<2.9.0",  # zhipuai兼容性
            "torch": ">=2.1.0,<3.0.0",
            "transformers": ">=4.36.0,<5.0.0",
            "langchain": ">=0.1.0,<1.0.0",
            "langchain-core": ">=0.1.0,<1.0.0",
            "langchain-openai": ">=0.1.0,<1.0.0",
            # 其他服务版本冲突修复
            "grpcio": ">=1.59.0",  # corn-maze-service
            "aiohttp": ">=3.9.1",  # message-bus
            "grpcio-tools": ">=1.59.0",
            "grpcio-health-checking": ">=1.59.0",
            "grpcio-reflection": ">=1.59.0",
        }

    def fix_requirements_file(self, file_path: Path) -> bool:
        """修复requirements.txt文件"""
        if not file_path.exists():
            return False

        print(f"修复文件: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        fixed_lines = []
        for line in lines:
            line = line.strip()

            # 跳过空行和注释
            if not line or line.startswith('#'):
                fixed_lines.append(line)
                continue

            # 检查是否有格式错误（如HTML标签）
            if '<' in line and not any(op in line for op in ['>=', '<=', '==', '!=', '~=']):
                print(f"  跳过格式错误的行: {line}")
                continue

            # 修复版本冲突
            for package, new_version in self.version_map.items():
                if line.startswith(package):
                    # 提取包名和版本
                    match = re.match(r'^([a-zA-Z0-9\-_\[\]]+)([><=!~]+.*)?$', line)
                    if match:
                        pkg_name = match.group(1)
                        if pkg_name == package:
                            line = f"{package}{new_version}"
                            print(f"  更新版本: {package} -> {new_version}")
                            break

            fixed_lines.append(line)

        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            for line in fixed_lines:
                f.write(line + '\n')

        return True

    def create_clean_requirements(self, service_path: Path) -> bool:
        """为服务创建清理后的requirements.txt"""
        requirements_file = service_path / "requirements.txt"
        if not requirements_file.exists():
            return False

        # 创建简化版本用于测试
        clean_requirements = service_path / "requirements-clean.txt"

        with open(requirements_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        clean_lines = []
        for line in lines:
            line = line.strip()

            # 跳过空行、注释和测试依赖
            if (not line or line.startswith('#') or 
                any(test_pkg in line.lower() for test_pkg in ['pytest', 'black', 'isort', 'flake8', 'mypy'])):
                continue

            # 跳过格式错误的行
            if '<' in line and not any(op in line for op in ['>=', '<=', '==', '!=', '~=']):
                continue

            clean_lines.append(line)

        with open(clean_requirements, 'w', encoding='utf-8') as f:
            for line in clean_lines:
                f.write(line + '\n')

        print(f"创建清理版本: {clean_requirements}")
        return True

    def fix_service(self, service_name: str) -> bool:
        """修复单个服务的依赖"""
        service_path = self.services_dir / service_name
        if not service_path.exists():
            print(f"服务不存在: {service_name}")
            return False

        print(f"\n修复服务: {service_name}")

        # 修复requirements.txt
        requirements_file = service_path / "requirements.txt"
        if requirements_file.exists():
            self.fix_requirements_file(requirements_file)
            self.create_clean_requirements(service_path)

        # 修复pyproject.toml中的依赖
        pyproject_file = service_path / "pyproject.toml"
        if pyproject_file.exists():
            self.fix_pyproject_dependencies(pyproject_file)

        return True

    def fix_pyproject_dependencies(self, file_path: Path) -> bool:
        """修复pyproject.toml中的依赖版本"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 更新依赖版本
        for package, new_version in self.version_map.items():
            # 匹配依赖行
            pattern = rf'"{package}[^"]*"'
            replacement = f'"{package}{new_version}"'
            content = re.sub(pattern, replacement, content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  更新pyproject.toml: {file_path}")
        return True

    def fix_all_services(self) -> Dict[str, bool]:
        """修复所有服务的依赖"""
        results = {}

        services_to_fix = [
            "auth-service",
            "api-gateway", 
            "user-service",
            "blockchain-service",
            "health-data-service",
            "corn-maze-service",
            # 智能体服务
            "agent-services/xiaoai-service",
            "agent-services/xiaoke-service", 
            "agent-services/laoke-service",
            "agent-services/soer-service",
            # 其他需要修复的服务
            "message-bus",
        ]

        for service in services_to_fix:
            results[service] = self.fix_service(service)

        return results

def main():
    fixer = DependencyFixer(".")

    print("🔧 开始修复索克生活项目依赖冲突...")

    results = fixer.fix_all_services()

    print("\n📊 修复结果:")
    for service, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {service}: {status}")

    print("\n✨ 依赖修复完成！")

if __name__ == "__main__":
    main() 