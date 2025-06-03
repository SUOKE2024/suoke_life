#!/usr/bin/env python3
"""
RAG Service UV 配置验证脚本
验证 UV 包管理器配置是否正确
"""

import sys
import subprocess
from pathlib import Path
import tomllib

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 13, 3):
        print("✓ Python 版本符合要求 (>=3.13.3)")
        return True
    else:
        print("✗ Python 版本不符合要求，需要 >=3.13.3")
        return False

def check_uv_installation():
    """检查 UV 是否安装"""
    try:
        result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ UV 已安装: {result.stdout.strip()}")
            return True
        else:
            print("✗ UV 未正确安装")
            return False
    except FileNotFoundError:
        print("✗ UV 未安装")
        return False

def check_pyproject_toml():
    """检查 pyproject.toml 配置"""
    pyproject_path = Path("pyproject.toml")
    
    if not pyproject_path.exists():
        print("✗ pyproject.toml 文件不存在")
        return False
    
    try:
        with open(pyproject_path, "rb") as f:
            config = tomllib.load(f)
        
        # 检查基本配置
        if "project" in config:
            project = config["project"]
            print(f"✓ 项目名称: {project.get('name', 'N/A')}")
            print(f"✓ 项目版本: {project.get('version', 'N/A')}")
            print(f"✓ Python 要求: {project.get('requires-python', 'N/A')}")
            
            # 检查依赖数量
            deps = project.get('dependencies', [])
            print(f"✓ 生产依赖数量: {len(deps)}")
            
            # 检查开发依赖
            dev_deps = project.get('optional-dependencies', {}).get('dev', [])
            print(f"✓ 开发依赖数量: {len(dev_deps)}")
        
        # 检查 UV 配置
        if "tool" in config and "uv" in config["tool"]:
            uv_config = config["tool"]["uv"]
            index_url = uv_config.get("index-url", "")
            if "tuna.tsinghua.edu.cn" in index_url:
                print("✓ UV 配置使用国内镜像源")
            else:
                print("⚠ UV 配置未使用国内镜像源")
        
        # 检查代码质量工具配置
        tools = ["ruff", "black", "mypy", "pytest"]
        for tool in tools:
            if "tool" in config and tool in config["tool"]:
                print(f"✓ {tool.capitalize()} 配置已设置")
            else:
                print(f"⚠ {tool.capitalize()} 配置缺失")
        
        return True
        
    except Exception as e:
        print(f"✗ pyproject.toml 解析错误: {e}")
        return False

def check_uvrc():
    """检查 .uvrc 配置文件"""
    uvrc_path = Path(".uvrc")
    
    if not uvrc_path.exists():
        print("⚠ .uvrc 文件不存在")
        return False
    
    try:
        content = uvrc_path.read_text()
        if "tuna.tsinghua.edu.cn" in content:
            print("✓ .uvrc 配置使用国内镜像源")
            return True
        else:
            print("⚠ .uvrc 配置未使用国内镜像源")
            return False
    except Exception as e:
        print(f"✗ .uvrc 读取错误: {e}")
        return False

def check_makefile():
    """检查 Makefile 配置"""
    makefile_path = Path("Makefile")
    
    if not makefile_path.exists():
        print("✗ Makefile 不存在")
        return False
    
    try:
        content = makefile_path.read_text()
        
        # 检查 UV 相关命令
        uv_commands = ["uv-install", "uv-sync", "uv-update", "uv-dev"]
        for cmd in uv_commands:
            if cmd in content:
                print(f"✓ Makefile 包含 {cmd} 命令")
            else:
                print(f"⚠ Makefile 缺少 {cmd} 命令")
        
        return True
        
    except Exception as e:
        print(f"✗ Makefile 读取错误: {e}")
        return False

def check_dockerfile():
    """检查 Dockerfile.uv"""
    dockerfile_path = Path("Dockerfile.uv")
    
    if not dockerfile_path.exists():
        print("✗ Dockerfile.uv 不存在")
        return False
    
    try:
        content = dockerfile_path.read_text()
        
        if "python:3.13.3" in content:
            print("✓ Dockerfile.uv 使用 Python 3.13.3")
        else:
            print("⚠ Dockerfile.uv 未使用 Python 3.13.3")
        
        if "tuna.tsinghua.edu.cn" in content:
            print("✓ Dockerfile.uv 使用国内镜像源")
        else:
            print("⚠ Dockerfile.uv 未使用国内镜像源")
        
        if "uv sync" in content:
            print("✓ Dockerfile.uv 使用 UV 包管理")
        else:
            print("⚠ Dockerfile.uv 未使用 UV 包管理")
        
        return True
        
    except Exception as e:
        print(f"✗ Dockerfile.uv 读取错误: {e}")
        return False

def main():
    """主验证函数"""
    print("=" * 60)
    print("RAG Service UV 配置验证")
    print("=" * 60)
    
    checks = [
        ("Python 版本检查", check_python_version),
        ("UV 安装检查", check_uv_installation),
        ("pyproject.toml 检查", check_pyproject_toml),
        (".uvrc 配置检查", check_uvrc),
        ("Makefile 检查", check_makefile),
        ("Dockerfile.uv 检查", check_dockerfile),
    ]
    
    results = []
    
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 40)
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ 检查失败: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("验证总结:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总体结果: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("🎉 所有检查都通过！RAG Service UV 配置完成。")
        return 0
    else:
        print("⚠️  部分检查未通过，请查看上述详细信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 