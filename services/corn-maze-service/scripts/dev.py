#!/usr/bin/env python3
"""
开发工具脚本

提供开发、测试、代码检查等常用命令
"""

from pathlib import Path
import subprocess
import sys

from corn_maze_service.constants import MIN_COMMAND_ARGS


def run_command(cmd: list[str], cwd: Path | None = None) -> int:
    """运行命令"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, check=False)
    return result.returncode

def install():
    """安装依赖"""
    return run_command(["uv", "sync"])

def server():
    """启动服务器"""
    return run_command(["uv", "run", "python", "-m", "corn_maze_service.cmd.server.main"])

def test():
    """运行测试"""
    return run_command(["uv", "run", "pytest", "-v"])

def lint():
    """代码检查"""
    return run_command(["uv", "run", "ruff", "check", "."])

def format_code():
    """格式化代码"""
    return run_command(["uv", "run", "ruff", "format", "."])

def type_check():
    """类型检查"""
    return run_command(["uv", "run", "mypy", "."])

def run_tests():
    """运行测试"""
    return run_command(["uv", "run", "pytest", "-v", "--cov=corn_maze_service"])

def check_all():
    """运行所有检查"""
    checks = [
        ("代码检查", lint),
        ("类型检查", type_check),
        ("测试", run_tests),
    ]

    for name, check_func in checks:
        print(f"\n=== {name} ===")
        result = check_func()
        if result != 0:
            print(f"❌ {name} 失败")
            return 1
        print(f"✅ {name} 通过")

    print("\n🎉 所有检查都通过了!")
    return 0

def main():
    """主函数"""
    if len(sys.argv) < MIN_COMMAND_ARGS:
        print("Usage: python scripts/dev.py <command>")
        print("Commands: install, server, test, lint, format, type-check, check")
        return 1

    command = sys.argv[1]
    commands = {
        "install": install,
        "server": server,
        "test": test,
        "lint": lint,
        "format": format_code,
        "type-check": type_check,
        "check": check_all,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        return 1

    return commands[command]()

if __name__ == "__main__":
    sys.exit(main())
