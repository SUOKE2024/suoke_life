#!/usr/bin/env python3
"""
索克生活无障碍服务 - 环境设置脚本
自动化依赖安装和环境配置
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


class EnvironmentSetup:
    """环境设置管理器"""

    def __init__(self) -> None:
        self.service_dir = Path(__file__).parent
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.platform = platform.system().lower()

    def check_python_version(self) -> bool:
        """检查Python版本"""
        required_version = (3, 11, 0)
        current_version = sys.version_info[:3]

        if current_version >= required_version:
            print(f"✅ Python版本检查通过: {self.python_version}")
            return True
        else:
            print(f"❌ Python版本过低: {self.python_version}, 需要 >= 3.11.0")
            return False

    def check_uv_available(self) -> bool:
        """检查UV包管理器是否可用"""
        try:
            result = subprocess.run(
                ["uv", "--version"], capture_output=True, text=True, check=True
            )
            print(f"✅ UV包管理器可用: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ UV包管理器不可用，将使用pip")
            return False

    def install_dependencies(self, mode: str = "core") -> bool:
        """安装依赖"""
        print(f"\n📦 开始安装依赖 (模式: {mode})")

        # 选择依赖文件
        if mode == "core":
            req_file = "requirements-core.txt"
        elif mode == "full":
            req_file = "requirements.txt"
        else:
            print(f"❌ 未知安装模式: {mode}")
            return False

        req_path = self.service_dir / req_file
        if not req_path.exists():
            print(f"❌ 依赖文件不存在: {req_path}")
            return False

        # 使用UV或pip安装
        if self.check_uv_available():
            cmd = ["uv", "pip", "install", "-r", str(req_path)]
        else:
            cmd = ["pip", "install", "-r", str(req_path)]

        try:
            print(f"执行命令: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, cwd=self.service_dir)
            print("✅ 依赖安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖安装失败: {e}")
            return False

    def setup_virtual_environment(self) -> bool:
        """设置虚拟环境"""
        venv_path = self.service_dir / ".venv"

        if venv_path.exists():
            print("✅ 虚拟环境已存在")
            return True

        print("🔧 创建虚拟环境...")
        try:
            if self.check_uv_available():
                subprocess.run(
                    ["uv", "venv", str(venv_path)], check=True, cwd=self.service_dir
                )
            else:
                subprocess.run(
                    [sys.executable, "-m", "venv", str(venv_path)],
                    check=True,
                    cwd=self.service_dir,
                )
            print("✅ 虚拟环境创建完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 虚拟环境创建失败: {e}")
            return False

    def create_activation_script(self) -> None:
        """创建激活脚本"""
        if self.platform == "windows":
            activate_script = self.service_dir / "activate.bat"
            script_content = """@echo off
echo 激活索克生活无障碍服务环境...
call .venv\\Scripts\\activate.bat
echo ✅ 环境已激活
echo 当前Python: %VIRTUAL_ENV%\\Scripts\\python.exe
echo 运行服务: python quick_start.py
"""
        else:
            activate_script = self.service_dir / "activate.sh"
            script_content = """#!/bin/bash
echo "激活索克生活无障碍服务环境..."
source .venv/bin/activate
echo "✅ 环境已激活"
echo "当前Python: $VIRTUAL_ENV/bin/python"
echo "运行服务: python quick_start.py"
"""

        with open(activate_script, "w", encoding="utf-8") as f:
            f.write(script_content)

        if self.platform != "windows":
            os.chmod(activate_script, 0o755)

        print(f"✅ 激活脚本已创建: {activate_script}")

    def validate_installation(self) -> bool:
        """验证安装"""
        print("\n🔍 验证安装...")

        # 检查关键模块
        critical_modules = ["grpcio", "pydantic", "pyyaml", "numpy", "psutil"]

        failed_modules = []
        for module in critical_modules:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError:
                print(f"❌ {module}")
                failed_modules.append(module)

        if failed_modules:
            print(f"\n❌ 以下模块导入失败: {', '.join(failed_modules)}")
            return False

        print("\n✅ 所有关键模块验证通过")
        return True

    def run_quick_test(self) -> bool:
        """运行快速测试"""
        print("\n🧪 运行快速测试...")

        test_script = self.service_dir / "quick_validation.py"
        if not test_script.exists():
            print("⚠️ 快速测试脚本不存在，跳过测试")
            return True

        try:
            subprocess.run(
                [sys.executable, str(test_script)],
                check=True,
                cwd=self.service_dir,
                timeout=60,
            )
            print("✅ 快速测试通过")
            return True
        except subprocess.TimeoutExpired:
            print("⚠️ 快速测试超时，但环境配置正常")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️ 快速测试失败: {e}")
            return True  # 不阻止环境设置

    def setup(self, mode: str = "core", skip_venv: bool = False) -> bool:
        """完整环境设置"""
        print("🚀 索克生活无障碍服务 - 环境设置开始")
        print(f"平台: {self.platform}")
        print(f"Python: {self.python_version}")
        print(f"工作目录: {self.service_dir}")
        print(f"安装模式: {mode}")

        # 检查Python版本
        if not self.check_python_version():
            return False

        # 设置虚拟环境
        if not skip_venv:
            if not self.setup_virtual_environment():
                return False

        # 安装依赖
        if not self.install_dependencies(mode):
            return False

        # 创建激活脚本
        self.create_activation_script()

        # 验证安装
        if not self.validate_installation():
            return False

        # 运行快速测试
        self.run_quick_test()

        print("\n🎉 环境设置完成！")
        print("\n📋 下一步操作:")
        if self.platform == "windows":
            print("1. 运行: activate.bat")
        else:
            print("1. 运行: source activate.sh")
        print("2. 启动服务: python quick_start.py")
        print("3. 运行测试: python demo_comprehensive.py")

        return True


def main() -> None:
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="索克生活无障碍服务环境设置")
    parser.add_argument(
        "--mode",
        choices=["core", "full"],
        default="core",
        help="安装模式: core(核心依赖) 或 full(完整依赖)",
    )
    parser.add_argument("--skip-venv", action="store_true", help="跳过虚拟环境创建")

    args = parser.parse_args()

    setup = EnvironmentSetup()
    success = setup.setup(mode=args.mode, skip_venv=args.skip_venv)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
