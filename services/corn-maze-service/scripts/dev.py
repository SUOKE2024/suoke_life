#!/usr/bin/env python3
"""
开发脚本

提供开发环境的常用命令。
"""

import argparse
from pathlib import Path
import subprocess
import sys


def run_command(cmd: list[str], cwd: Path = None) -> int:
    """运行命令"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, check=False)
    return result.returncode


def install_deps() -> int:
    """安装依赖"""
    return run_command(["uv", "sync", "--dev"])


def run_server() -> int:
    """运行服务器"""
    return run_command(["uv", "run", "python", "-m", "corn_maze_service.cmd.server.main"])


def run_tests() -> int:
    """运行测试"""
    return run_command(["uv", "run", "pytest", "tests/", "-v"])


def run_lint() -> int:
    """运行代码检查"""
    # 只检查主要代码，忽略测试文件中的魔法数字
    return run_command(["uv", "run", "ruff", "check", "corn_maze_service/"])


def run_format() -> int:
    """格式化代码"""
    return run_command(["uv", "run", "ruff", "format", "corn_maze_service/", "tests/"])


def run_type_check() -> int:
    """运行类型检查"""
    return run_command(["uv", "run", "mypy", "corn_maze_service", "--strict"])


def run_all_checks() -> int:
    """运行所有检查"""
    checks = [
        ("代码检查", run_lint),
        ("类型检查", run_type_check),
        ("测试", run_tests),
    ]
    
    for name, check_func in checks:
        print(f"\n=== {name} ===")
        if check_func() != 0:
            print(f"❌ {name} 失败")
            return 1
        print(f"✅ {name} 通过")
    
    print("\n🎉 所有检查都通过了！")
    return 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="开发脚本")
    parser.add_argument(
        "command",
        choices=["install", "server", "test", "lint", "format", "type-check", "check"],
        help="要执行的命令"
    )

    args = parser.parse_args()

    commands = {
        "install": install_deps,
        "server": run_server,
        "test": run_tests,
        "lint": run_lint,
        "format": run_format,
        "type-check": run_type_check,
        "check": run_all_checks,
    }

    exit_code = commands[args.command]()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
