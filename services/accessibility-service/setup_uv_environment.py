#!/usr/bin/env python3.13

"""
UV 环境管理脚本
用于设置和管理 Python UV 虚拟环境

功能：
1. 检查系统要求
2. 安装 UV 包管理器
3. 创建虚拟环境
4. 安装项目依赖
5. 安装开发工具
6. 生成环境激活脚本
"""

import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class UVEnvironmentManager:
    """UV 环境管理器"""

    def __init__(self, service_path: str):
        self.service_path = Path(service_path)
        self.venv_path = self.service_path / ".venv"
        self.results = []
        self.start_time = time.time()

    def log_step(self, step: str, success: bool, message: str, error: str = None):
        """记录步骤结果"""
        status = "✅" if success else "❌"
        print(f"{status} {step}: {message}")
        if error:
            print(f"   错误: {error}")

        self.results.append(
            {
                "step": step,
                "success": success,
                "message": message,
                "error": error,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def run_command(
        self, command: list[str], timeout: int = 300, shell: bool = False
    ) -> tuple[bool, str, str]:
        """运行命令"""
        try:
            if shell and isinstance(command, list):
                command = " ".join(command)

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.service_path,
                shell=shell,
                encoding="utf-8",
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"命令超时 ({timeout}s)"
        except Exception as e:
            return False, "", str(e)

    def check_system_requirements(self) -> None:
        """检查系统要求"""
        print("🔍 检查系统要求...")

        # 检查 Python 版本
        version = platform.python_version()
        major, minor, patch = map(int, version.split("."))

        if major == 3 and minor >= 13:
            self.log_step("Python 版本", True, f"Python {version}")
        else:
            self.log_step("Python 版本", False, f"Python {version} (需要 3.13+)")
            return False

        # 检查操作系统
        system = platform.system()
        self.log_step("操作系统", True, f"{system} {platform.release()}")

        # 检查网络连接（通过 ping）
        if system == "Windows":
            success, _, _ = self.run_command(
                ["ping", "-n", "1", "pypi.org"], timeout=10
            )
        else:
            success, _, _ = self.run_command(
                ["ping", "-c", "1", "pypi.org"], timeout=10
            )

        self.log_step(
            "网络连接", success, "网络连接正常" if success else "网络连接异常"
        )

        return True

    def install_uv(self) -> None:
        """安装 UV 包管理器"""
        print("\n📦 安装 UV 包管理器...")

        # 检查是否已安装
        success, stdout, _ = self.run_command(["uv", "--version"])
        if success:
            version = stdout.strip()
            self.log_step("UV 检查", True, f"UV 已安装: {version}")
            return True

        # 安装 UV
        system = platform.system()

        if system in ["Linux", "Darwin"]:  # Linux 或 macOS
            install_cmd = ["curl", "-LsSf", "https://astral.sh/uv/install.sh"]
            success, stdout, stderr = self.run_command(install_cmd, shell=True)

            if success:
                # 运行安装脚本
                success, stdout, stderr = self.run_command(["sh"], shell=True)

        elif system == "Windows":
            # Windows 安装
            install_cmd = [
                "powershell",
                "-c",
                "irm https://astral.sh/uv/install.ps1 | iex",
            ]
            success, stdout, stderr = self.run_command(install_cmd, shell=True)

        else:
            self.log_step("UV 安装", False, f"不支持的操作系统: {system}")
            return False

        if success:
            # 验证安装
            success, stdout, _ = self.run_command(["uv", "--version"])
            if success:
                version = stdout.strip()
                self.log_step("UV 安装", True, f"UV 安装成功: {version}")
                return True

        self.log_step("UV 安装", False, "UV 安装失败", stderr)
        return False

    def create_virtual_environment(self) -> None:
        """创建虚拟环境"""
        print("\n🏗️  创建虚拟环境...")

        # 删除现有虚拟环境（如果存在）
        if self.venv_path.exists():
            import shutil

            shutil.rmtree(self.venv_path)
            self.log_step("清理环境", True, "删除现有虚拟环境")

        # 创建新的虚拟环境
        success, stdout, stderr = self.run_command(
            ["uv", "venv", str(self.venv_path), "--python", "3.13"]
        )

        if success:
            self.log_step("创建虚拟环境", True, f"虚拟环境创建成功: {self.venv_path}")
            return True
        else:
            self.log_step("创建虚拟环境", False, "虚拟环境创建失败", stderr)
            return False

    def install_dependencies(self) -> None:
        """安装项目依赖"""
        print("\n📚 安装项目依赖...")

        # 检查 requirements.txt
        requirements_file = self.service_path / "requirements.txt"
        if not requirements_file.exists():
            self.log_step("依赖文件", False, "requirements.txt 不存在")
            return False

        # 安装核心依赖
        success, stdout, stderr = self.run_command(
            ["uv", "pip", "install", "-r", str(requirements_file)]
        )

        if success:
            self.log_step("核心依赖", True, "核心依赖安装成功")
        else:
            self.log_step("核心依赖", False, "核心依赖安装失败", stderr)
            return False

        # 安装开发依赖（如果存在 pyproject.toml）
        pyproject_file = self.service_path / "pyproject.toml"
        if pyproject_file.exists():
            success, stdout, stderr = self.run_command(
                ["uv", "pip", "install", "-e", ".[dev]"]
            )

            if success:
                self.log_step("开发依赖", True, "开发依赖安装成功")
            else:
                self.log_step("开发依赖", False, "开发依赖安装失败", stderr)

        return True

    def install_development_tools(self) -> None:
        """安装开发工具"""
        print("\n🛠️  安装开发工具...")

        dev_tools = [
            "black",  # 代码格式化
            "ruff",  # 代码检查
            "mypy",  # 类型检查
            "pytest",  # 测试框架
            "pytest-cov",  # 测试覆盖率
        ]

        for tool in dev_tools:
            success, stdout, stderr = self.run_command(["uv", "pip", "install", tool])

            if success:
                self.log_step(f"工具 {tool}", True, f"{tool} 安装成功")
            else:
                self.log_step(f"工具 {tool}", False, f"{tool} 安装失败", stderr)

    def generate_activation_script(self) -> None:
        """生成环境激活脚本"""
        print("\n📝 生成环境激活脚本...")

        # 生成 Unix/Linux/macOS 激活脚本
        unix_script = f"""#!/bin/bash
# 无障碍服务环境激活脚本

echo "🚀 激活无障碍服务开发环境..."

# 激活虚拟环境
source {self.venv_path}/bin/activate

# 设置环境变量
export PYTHONPATH="{self.service_path}:$PYTHONPATH"
export ACCESSIBILITY_CONFIG_PATH="{self.service_path}/config/config.yaml"

echo "✅ 环境已激活!"
echo "📁 项目路径: {self.service_path}"
echo "🐍 Python 路径: $(which python)"
echo "📦 虚拟环境: {self.venv_path}"

# 显示可用命令
echo ""
echo "🛠️  可用命令:"
echo "  python cmd/server/main.py          # 启动服务"
echo "  python quick_validation.py         # 快速验证"
echo "  python -m pytest                   # 运行测试"
echo "  python -m black .                  # 格式化代码"
echo "  python -m ruff check .             # 检查代码质量"
echo ""
"""

        # 生成 Windows 激活脚本
        windows_script = f"""@echo off
REM 无障碍服务环境激活脚本

echo 🚀 激活无障碍服务开发环境...

REM 激活虚拟环境
call {self.venv_path}\\Scripts\\activate.bat

REM 设置环境变量
set PYTHONPATH={self.service_path};%PYTHONPATH%
set ACCESSIBILITY_CONFIG_PATH={self.service_path}\\config\\config.yaml

echo ✅ 环境已激活!
echo 📁 项目路径: {self.service_path}
echo 🐍 Python 路径: %VIRTUAL_ENV%\\Scripts\\python.exe
echo 📦 虚拟环境: {self.venv_path}

echo.
echo 🛠️  可用命令:
echo   python cmd\\server\\main.py          # 启动服务
echo   python quick_validation.py         # 快速验证
echo   python -m pytest                   # 运行测试
echo   python -m black .                  # 格式化代码
echo   python -m ruff check .             # 检查代码质量
echo.
"""

        # 保存脚本
        try:
            # Unix/Linux/macOS 脚本
            unix_script_path = self.service_path / "activate_env.sh"
            with open(unix_script_path, "w", encoding="utf-8") as f:
                f.write(unix_script)
            os.chmod(unix_script_path, 0o755)  # 添加执行权限

            # Windows 脚本
            windows_script_path = self.service_path / "activate_env.bat"
            with open(windows_script_path, "w", encoding="utf-8") as f:
                f.write(windows_script)

            self.log_step("激活脚本", True, "环境激活脚本生成成功")
            return True
        except Exception as e:
            self.log_step("激活脚本", False, "激活脚本生成失败", str(e))
            return False

    def generate_environment_info(self) -> None:
        """生成环境信息文件"""
        print("\n📋 生成环境信息...")

        # 获取已安装包列表
        success, stdout, stderr = self.run_command(
            ["uv", "pip", "list", "--format", "json"]
        )

        packages = []
        if success:
            try:
                packages = json.loads(stdout)
            except json.JSONDecodeError:
                packages = []

        # 生成环境信息
        env_info = {
            "timestamp": datetime.now().isoformat(),
            "python_version": platform.python_version(),
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            },
            "paths": {
                "service_path": str(self.service_path),
                "venv_path": str(self.venv_path),
                "python_executable": (
                    str(self.venv_path / "bin" / "python")
                    if platform.system() != "Windows"
                    else str(self.venv_path / "Scripts" / "python.exe")
                ),
            },
            "packages": packages,
            "setup_results": self.results,
        }

        # 保存环境信息
        try:
            info_file = self.service_path / "environment_info.json"
            with open(info_file, "w", encoding="utf-8") as f:
                json.dump(env_info, f, indent=2, ensure_ascii=False)

            self.log_step("环境信息", True, f"环境信息已保存: {info_file}")
            return True
        except Exception as e:
            self.log_step("环境信息", False, "环境信息保存失败", str(e))
            return False

    def setup_environment(self) -> None:
        """设置完整环境"""
        print("🚀 开始设置 UV 开发环境...")
        print(f"📁 服务路径: {self.service_path}")
        print("=" * 60)

        # 执行所有设置步骤
        steps = [
            self.check_system_requirements,
            self.install_uv,
            self.create_virtual_environment,
            self.install_dependencies,
            self.install_development_tools,
            self.generate_activation_script,
            self.generate_environment_info,
        ]

        for step in steps:
            if not step():
                print(f"\n❌ 设置失败于步骤: {step.__name__}")
                return False

        # 统计结果
        total_steps = len(self.results)
        successful_steps = sum(1 for r in self.results if r["success"])
        duration = time.time() - self.start_time

        print("\n" + "=" * 60)
        print("🎉 环境设置完成!")
        print(f"✅ 成功步骤: {successful_steps}/{total_steps}")
        print(f"⏱️  总耗时: {duration:.2f}s")
        print(f"📁 虚拟环境: {self.venv_path}")

        # 显示使用说明
        print("\n🛠️  使用说明:")
        if platform.system() == "Windows":
            print("  1. 运行: activate_env.bat")
        else:
            print("  1. 运行: source activate_env.sh")
        print("  2. 验证: python quick_validation.py")
        print("  3. 启动: python cmd/server/main.py")

        return True


def main() -> None:
    """主函数"""
    service_path = os.path.dirname(os.path.abspath(__file__))
    manager = UVEnvironmentManager(service_path)
    success = manager.setup_environment()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
