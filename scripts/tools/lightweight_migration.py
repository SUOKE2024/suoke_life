#!/usr/bin/env python3
"""
索克生活项目 - 轻量级uv迁移脚本
专门处理包含大型AI/ML依赖的服务，采用分阶段安装策略
"""

import subprocess
import time
from pathlib import Path
from typing import List, Dict

class LightweightMigrator:
    """轻量级迁移器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.services_dir = self.project_root / "services"

        # 核心依赖（快速安装）
        self.core_deps = [
            "fastapi>=0.115.0",
            "uvicorn>=0.32.0",
            "pydantic>=2.10.0",
            "pydantic-settings>=2.6.0",
            "httpx>=0.28.0",
            "redis>=5.2.0",
            "sqlalchemy>=2.0.36",
            "asyncpg>=0.30.0",
            "python-dotenv>=1.0.1",
            "pyyaml>=6.0.2",
            "loguru>=0.7.2",
            "tenacity>=9.0.0",
        ]

        # AI/ML依赖（可选安装）
        self.ai_deps = [
            "torch>=2.1.0,<3.0.0",
            "transformers>=4.36.0,<5.0.0",
            "sentence-transformers>=3.3.0",
            "langchain>=0.1.0,<1.0.0",
            "langchain-core>=0.1.0,<1.0.0",
            "langchain-openai>=0.1.0,<1.0.0",
            "openai>=1.54.0",
            "anthropic>=0.40.0",
            "numpy>=2.1.0",
            "scipy>=1.14.0",
        ]

    def create_minimal_pyproject(self, service_path: Path, service_name: str) -> bool:
        """创建最小化的pyproject.toml"""
        config = f'''[project]
name = "{service_name}"
version = "1.0.0"
description = "{service_name} - 索克生活智能体服务"
requires-python = ">=3.11"
dependencies = [
    # 核心Web框架
    "fastapi>=0.115.0,<1.0.0",
    "uvicorn[standard]>=0.32.0,<1.0.0",
    "pydantic>=2.10.0,<3.0.0",
    "pydantic-settings>=2.6.0,<3.0.0",

    # 数据库和缓存
    "sqlalchemy>=2.0.36,<3.0.0",
    "asyncpg>=0.30.0,<1.0.0",
    "redis>=5.2.0,<6.0.0",

    # HTTP客户端
    "httpx>=0.28.0,<1.0.0",
    "aiohttp>=3.10.0,<4.0.0",

    # 配置和日志
    "python-dotenv>=1.0.1,<2.0.0",
    "pyyaml>=6.0.2,<7.0.0",
    "loguru>=0.7.2,<1.0.0",

    # 工具库
    "tenacity>=9.0.0,<10.0.0",
    "ujson>=5.10.0,<6.0.0",
    "python-multipart>=0.0.12,<1.0.0",
]

[project.optional-dependencies]
ai = [
    # AI/ML依赖 - 可选安装
    "torch>=2.1.0,<3.0.0",
    "transformers>=4.36.0,<5.0.0",
    "sentence-transformers>=3.3.0,<4.0.0",
    "langchain>=0.1.0,<1.0.0",
    "langchain-core>=0.1.0,<1.0.0",
    "langchain-openai>=0.1.0,<1.0.0",
    "openai>=1.54.0,<2.0.0",
    "anthropic>=0.40.0,<1.0.0",
    "numpy>=2.1.0,<3.0.0",
    "scipy>=1.14.0,<2.0.0",
]

dev = [
    "pytest>=8.3.0,<9.0.0",
    "pytest-asyncio>=0.24.0,<1.0.0",
    "pytest-cov>=6.0.0,<7.0.0",
    "black>=24.10.0,<25.0.0",
    "isort>=5.13.0,<6.0.0",
    "mypy>=1.13.0,<2.0.0",
]

[tool.black]
line-length = 88
target-version = ['py311', 'py312', 'py313']

[tool.isort]
profile = "black"
line_length = 88

[tool.pytest.ini_options]
testpaths = ["test"]
python_files = "test_*.py"
asyncio_mode = "auto"
'''

        pyproject_path = service_path / "pyproject-minimal.toml"
        with open(pyproject_path, 'w', encoding='utf-8') as f:
            f.write(config)

        print(f"✅ 创建最小化配置: {pyproject_path}")
        return True

    def migrate_service_lightweight(self, service_path: Path) -> bool:
        """轻量级迁移单个服务"""
        service_name = service_path.name
        print(f"\n🚀 开始轻量级迁移: {service_name}")

        # 备份原始配置
        if (service_path / "pyproject.toml").exists():
            backup_path = service_path / "pyproject-original.toml"
            subprocess.run(["cp", str(service_path / "pyproject.toml"), str(backup_path)])
            print(f"  📦 备份原始配置: {backup_path}")

        # 创建最小化配置
        self.create_minimal_pyproject(service_path, service_name)

        # 使用最小化配置初始化
        try:
            result = subprocess.run(
                ["uv", "init", "--no-readme"],
                cwd=service_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print(f"  ✅ uv初始化成功")
            else:
                print(f"  ❌ uv初始化失败: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print(f"  ⏰ uv初始化超时")
            return False

        # 安装核心依赖（快速）
        try:
            print(f"  📦 安装核心依赖...")
            result = subprocess.run(
                ["uv", "sync", "--no-dev"],
                cwd=service_path,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            if result.returncode == 0:
                print(f"  ✅ 核心依赖安装成功")
            else:
                print(f"  ⚠️  核心依赖安装有问题，但继续: {result.stderr[:200]}...")
        except subprocess.TimeoutExpired:
            print(f"  ⏰ 核心依赖安装超时，跳过")

        # 创建AI依赖安装脚本
        install_ai_script = service_path / "install_ai_deps.sh"
        script_content = f'''#!/bin/bash
# {service_name} AI依赖安装脚本
echo "🤖 开始安装AI/ML依赖..."
echo "⚠️  这可能需要较长时间，请耐心等待..."

cd "{service_path}"

# 安装AI依赖（可选）
uv sync --extra ai --no-dev

echo "✅ AI依赖安装完成！"
'''

        with open(install_ai_script, 'w') as f:
            f.write(script_content)

        # 设置执行权限
        subprocess.run(["chmod", "+x", str(install_ai_script)])
        print(f"  📝 创建AI依赖安装脚本: {install_ai_script}")

        return True

    def migrate_agent_services(self) -> Dict[str, bool]:
        """迁移所有智能体服务"""
        results = {}

        agent_services = [
            "agent-services/xiaoai-service",
            "agent-services/xiaoke-service",
            "agent-services/laoke-service",
            "agent-services/soer-service",
        ]

        for service_name in agent_services:
            service_path = self.services_dir / service_name
            if service_path.exists():
                try:
                    success = self.migrate_service_lightweight(service_path)
                    results[service_name] = success
                except Exception as e:
                    print(f"  ❌ 迁移失败: {str(e)}")
                    results[service_name] = False
            else:
                print(f"  ❌ 服务不存在: {service_name}")
                results[service_name] = False

        return results

    def create_batch_install_script(self) -> str:
        """创建批量AI依赖安装脚本"""
        script_path = self.project_root / "install_all_ai_deps.sh"

        script_content = '''#!/bin/bash
# 索克生活项目 - 批量AI依赖安装脚本
echo "🚀 开始批量安装所有智能体服务的AI依赖..."

SERVICES=(
    "services/agent-services/xiaoai-service"
    "services/agent-services/xiaoke-service"
    "services/agent-services/laoke-service"
    "services/agent-services/soer-service"
)

for service in "${SERVICES[@]}"; do
    if [ -d "$service" ]; then
        echo "📦 安装 $service 的AI依赖..."
        cd "$service"
        if [ -f "install_ai_deps.sh" ]; then
            ./install_ai_deps.sh
        else
            echo "⚠️  未找到AI依赖安装脚本"
        fi
        cd - > /dev/null
        echo "✅ $service 完成"
        echo "---"
    else
        echo "❌ 服务不存在: $service"
    fi
done

echo "🎉 所有智能体服务AI依赖安装完成！"
'''

        with open(script_path, 'w') as f:
            f.write(script_content)

        subprocess.run(["chmod", "+x", str(script_path)])
        return str(script_path)


def main():
    migrator = LightweightMigrator(".")

    print("🚀 开始索克生活智能体服务轻量级迁移...")
    print("📋 策略: 先安装核心依赖，AI/ML依赖单独安装")

    # 迁移智能体服务
    results = migrator.migrate_agent_services()

    # 创建批量安装脚本
    batch_script = migrator.create_batch_install_script()

    print("\n📊 迁移结果:")
    for service, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {service}: {status}")

    print(f"\n📝 批量AI依赖安装脚本: {batch_script}")
    print("\n💡 后续步骤:")
    print("1. 运行 ./install_all_ai_deps.sh 安装AI依赖（可选）")
    print("2. 或者单独运行各服务的 install_ai_deps.sh")
    print("3. 测试各服务功能")

    success_count = sum(results.values())
    total_count = len(results)
    print(f"\n🎉 轻量级迁移完成: {success_count}/{total_count} 服务成功迁移")


if __name__ == "__main__":
    main()