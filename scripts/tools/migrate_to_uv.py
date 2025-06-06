"""
migrate_to_uv - 索克生活项目模块
"""

from pathlib import Path
from typing import List, Dict, Optional
import argparse
import shutil
import subprocess
import sys
import time

#!/usr/bin/env python3
"""
索克生活项目 - uv迁移自动化脚本
自动将项目从pip/Poetry迁移到uv包管理器
"""


class UVMigrator:
    """uv迁移工具类"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.services_dir = self.project_root / "services"
        self.migration_log = []

    def log(self, message: str, level: str = "INFO"):
        """记录迁移日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.migration_log.append(log_entry)

    def run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> bool:
        """执行命令并返回是否成功"""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                self.log(f"命令执行成功: {' '.join(cmd)}")
                return True
            else:
                self.log(f"命令执行失败: {' '.join(cmd)}, 错误: {result.stderr}", "ERROR")
                return False
        except subprocess.TimeoutExpired:
            self.log(f"命令执行超时: {' '.join(cmd)}", "ERROR")
            return False
        except Exception as e:
            self.log(f"命令执行异常: {' '.join(cmd)}, 异常: {str(e)}", "ERROR")
            return False

    def check_uv_installed(self) -> bool:
        """检查uv是否已安装"""
        return self.run_command(["uv", "--version"])

    def install_uv(self) -> bool:
        """安装uv"""
        self.log("开始安装uv...")
        if sys.platform == "win32":
            # Windows安装
            cmd = ["powershell", "-c", "irm https://astral.sh/uv/install.ps1 | iex"]
        else:
            # Unix/Linux/macOS安装
            cmd = ["curl", "-LsSf", "https://astral.sh/uv/install.sh", "|", "sh"]

        return self.run_command(cmd)

    def backup_files(self, service_path: Path) -> bool:
        """备份原始文件"""
        backup_dir = service_path / "backup_before_uv"
        backup_dir.mkdir(exist_ok=True)

        files_to_backup = [
            "pyproject.toml",
            "poetry.lock",
            "requirements.txt",
            "Dockerfile"
        ]

        for file_name in files_to_backup:
            file_path = service_path / file_name
            if file_path.exists():
                shutil.copy2(file_path, backup_dir / file_name)
                self.log(f"备份文件: {file_path}")

        return True

    def convert_poetry_to_uv(self, service_path: Path) -> bool:
        """将Poetry配置转换为uv兼容格式"""
        pyproject_path = service_path / "pyproject.toml"
        if not pyproject_path.exists():
            return False

        # 读取现有配置
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 如果包含Poetry配置，进行转换
        if "[tool.poetry]" in content:
            self.log(f"转换Poetry配置: {service_path}")

            # 这里可以添加更复杂的转换逻辑
            # 目前简单地备份并创建新的配置
            self.backup_files(service_path)

            # 生成requirements.txt从poetry.lock
            if (service_path / "poetry.lock").exists():
                self.run_command(
                    ["poetry", "export", "-f", "requirements.txt",
                     "--output", "requirements.txt", "--without-hashes"],
                    cwd=service_path
                )

        return True

    def create_uv_config(self, service_path: Path, service_name: str) -> bool:
        """为服务创建uv兼容的pyproject.toml"""
        config_template = f'''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{service_name}"
version = "1.0.0"
description = "{service_name} - 索克生活平台微服务"
readme = "README.md"
authors = [
    {{name = "Suoke Life Team", email = "team@suokelife.com"}}
]
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.11.0",
    "isort>=5.12.0",
    "mypy>=1.7.0",
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

        pyproject_path = service_path / "pyproject.toml"
        with open(pyproject_path, 'w', encoding='utf-8') as f:
            f.write(config_template)

        self.log(f"创建uv配置: {pyproject_path}")
        return True

    def migrate_service(self, service_path: Path) -> bool:
        """迁移单个服务"""
        service_name = service_path.name
        self.log(f"开始迁移服务: {service_name}")

        # 备份原始文件
        self.backup_files(service_path)

        # 转换Poetry配置
        self.convert_poetry_to_uv(service_path)

        # 初始化uv项目
        if not self.run_command(["uv", "init", "--no-readme"], cwd=service_path):
            self.log(f"uv初始化失败: {service_name}", "ERROR")
            return False

        # 安装依赖
        requirements_file = service_path / "requirements.txt"
        if requirements_file.exists():
            if not self.run_command(["uv", "add", "-r", "requirements.txt"], cwd=service_path):
                self.log(f"依赖安装失败: {service_name}", "WARNING")

        # 生成锁定文件
        self.run_command(["uv", "lock"], cwd=service_path)

        self.log(f"服务迁移完成: {service_name}")
        return True

    def update_dockerfile(self, service_path: Path) -> bool:
        """更新Dockerfile使用uv"""
        dockerfile_path = service_path / "Dockerfile"
        if not dockerfile_path.exists():
            return False

        # 创建使用uv的新Dockerfile
        dockerfile_uv_content = '''# 使用uv的Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 复制项目文件
COPY pyproject.toml uv.lock* ./

# 安装依赖
RUN uv sync --frozen --no-dev

# 复制应用代码
COPY . .

# 设置环境变量
ENV PATH="/app/.venv/bin:$PATH"

# 运行应用
CMD ["python", "-m", "main"]
'''

        dockerfile_uv_path = service_path / "Dockerfile.uv"
        with open(dockerfile_uv_path, 'w', encoding='utf-8') as f:
            f.write(dockerfile_uv_content)

        self.log(f"创建uv Dockerfile: {dockerfile_uv_path}")
        return True

    def migrate_all_services(self) -> Dict[str, bool]:
        """迁移所有服务"""
        results = {}

        if not self.services_dir.exists():
            self.log("services目录不存在", "ERROR")
            return results

        for service_dir in self.services_dir.iterdir():
            if service_dir.is_dir() and not service_dir.name.startswith('.'):
                try:
                    success = self.migrate_service(service_dir)
                    results[service_dir.name] = success

                    # 更新Dockerfile
                    self.update_dockerfile(service_dir)

                except Exception as e:
                    self.log(f"迁移服务失败 {service_dir.name}: {str(e)}", "ERROR")
                    results[service_dir.name] = False

        return results

    def generate_migration_report(self, results: Dict[str, bool]) -> str:
        """生成迁移报告"""
        report = f"""
# 索克生活项目 - uv迁移报告

## 迁移概览
- 迁移时间: {time.strftime("%Y-%m-%d %H:%M:%S")}
- 总服务数: {len(results)}
- 成功迁移: {sum(results.values())}
- 失败迁移: {len(results) - sum(results.values())}

## 服务迁移状态
"""

        for service, success in results.items():
            status = "✅ 成功" if success else "❌ 失败"
            report += f"- {service}: {status}\n"

        report += f"""
## 迁移日志
```
{chr(10).join(self.migration_log)}
```

## 后续步骤
1. 测试各服务功能
2. 更新CI/CD流程
3. 更新文档
4. 性能对比测试
"""

        return report

    def run_migration(self, services: Optional[List[str]] = None) -> bool:
        """运行完整迁移流程"""
        self.log("开始索克生活项目uv迁移")

        # 检查uv安装
        if not self.check_uv_installed():
            self.log("uv未安装，开始安装...")
            if not self.install_uv():
                self.log("uv安装失败", "ERROR")
                return False

        # 迁移服务
        if services:
            results = {}
            for service in services:
                service_path = self.services_dir / service
                if service_path.exists():
                    results[service] = self.migrate_service(service_path)
                else:
                    self.log(f"服务不存在: {service}", "ERROR")
                    results[service] = False
        else:
            results = self.migrate_all_services()

        # 生成报告
        report = self.generate_migration_report(results)
        report_path = self.project_root / "uv_migration_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        self.log(f"迁移报告已生成: {report_path}")

        success_count = sum(results.values())
        total_count = len(results)
        self.log(f"迁移完成: {success_count}/{total_count} 服务成功迁移")

        return success_count == total_count

def main():
    parser = argparse.ArgumentParser(description="索克生活项目uv迁移工具")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--services", nargs="+", help="指定要迁移的服务")
    parser.add_argument("--dry-run", action="store_true", help="试运行模式")

    args = parser.parse_args()

    migrator = UVMigrator(args.project_root)

    if args.dry_run:
        print("试运行模式 - 不会实际修改文件")
        return

    success = migrator.run_migration(args.services)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()