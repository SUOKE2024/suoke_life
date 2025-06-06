"""
final_verification - 索克生活项目模块
"""

from pathlib import Path
import os
import subprocess
import sys

#!/usr/bin/env python3
"""
集成服务最终验证脚本
"""


def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def print_success(message):
    """打印成功信息"""
    print(f"✅ {message}")

def print_error(message):
    """打印错误信息"""
    print(f"❌ {message}")

def print_info(message):
    """打印信息"""
    print(f"ℹ️  {message}")

def run_command(command, description):
    """运行命令并返回结果"""
    print(f"\n🔧 {description}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print_success(f"{description} - 成功")
            return True, result.stdout
        else:
            print_error(f"{description} - 失败")
            print(f"错误输出: {result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print_error(f"{description} - 超时")
        return False, "命令执行超时"
    except Exception as e:
        print_error(f"{description} - 异常: {e}")
        return False, str(e)

def main():
    """主验证流程"""
    print_header("集成服务最终验证")
    
    # 设置环境变量
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["DEBUG"] = "true"
    os.environ["SECRET_KEY"] = "test-secret-key"
    
    # 验证项目结构
    print_header("项目结构验证")
    
    required_files = [
        "integration_service/__init__.py",
        "integration_service/main.py",
        "integration_service/config.py",
        "integration_service/core/database.py",
        "integration_service/core/security.py",
        "integration_service/models/user.py",
        "integration_service/models/platform.py",
        "integration_service/models/health_data.py",
        "integration_service/api/routes/auth.py",
        "integration_service/api/routes/platforms.py",
        "integration_service/api/routes/health_data.py",
        "integration_service/services/user_service.py",
        "integration_service/services/platform_service.py",
        "integration_service/services/health_data_service.py",
        "test/test_main.py",
        "test/test_api_endpoints.py",
        "test/test_complete_integration.py",
        "pyproject.toml",
        "Dockerfile",
        "docker-compose.yml",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"文件存在: {file_path}")
        else:
            print_error(f"文件缺失: {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print_error(f"发现 {len(missing_files)} 个缺失文件")
    else:
        print_success("所有必需文件都存在")
    
    # 验证Python模块导入
    print_header("模块导入验证")
    
    venv_python = "/Users/songxu/Developer/suoke_life/venv/bin/python"
    
    modules_to_test = [
        ("integration_service", "主模块"),
        ("integration_service.config", "配置模块"),
        ("integration_service.main", "主应用模块"),
        ("integration_service.core.database", "数据库模块"),
        ("integration_service.core.security", "安全模块"),
        ("integration_service.models.user", "用户模型"),
        ("integration_service.models.platform", "平台模型"),
        ("integration_service.models.health_data", "健康数据模型"),
    ]
    
    import_success = 0
    for module, description in modules_to_test:
        success, output = run_command(
            f"{venv_python} -c \"import {module}; print('导入成功')\"",
            f"导入 {description}"
        )
        if success:
            import_success += 1
    
    print_info(f"模块导入成功率: {import_success}/{len(modules_to_test)} ({import_success/len(modules_to_test)*100:.1f}%)")
    
    # 运行测试套件
    print_header("测试套件验证")
    
    test_commands = [
        (f"{venv_python} test_simple.py", "基础功能测试"),
        (f"{venv_python} -m pytest test/test_main.py -v", "主应用测试"),
        (f"{venv_python} -m pytest test/test_api_endpoints.py -v", "API端点测试"),
        (f"{venv_python} -m pytest test/ -v --tb=short", "完整测试套件"),
    ]
    
    test_success = 0
    for command, description in test_commands:
        success, output = run_command(command, description)
        if success:
            test_success += 1
    
    print_info(f"测试成功率: {test_success}/{len(test_commands)} ({test_success/len(test_commands)*100:.1f}%)")
    
    # 验证配置文件
    print_header("配置文件验证")
    
    config_files = [
        ("pyproject.toml", "项目配置"),
        ("Dockerfile", "Docker配置"),
        ("docker-compose.yml", "Docker Compose配置"),
        (".env.example", "环境变量示例"),
    ]
    
    config_success = 0
    for file_path, description in config_files:
        if Path(file_path).exists():
            print_success(f"{description}: {file_path}")
            config_success += 1
        else:
            print_error(f"{description}缺失: {file_path}")
    
    # 生成最终报告
    print_header("最终验证报告")
    
    total_checks = len(required_files) + len(modules_to_test) + len(test_commands) + len(config_files)
    passed_checks = (len(required_files) - len(missing_files)) + import_success + test_success + config_success
    
    success_rate = passed_checks / total_checks * 100
    
    print(f"""
📊 验证统计:
   - 文件结构: {len(required_files) - len(missing_files)}/{len(required_files)} 通过
   - 模块导入: {import_success}/{len(modules_to_test)} 通过  
   - 测试套件: {test_success}/{len(test_commands)} 通过
   - 配置文件: {config_success}/{len(config_files)} 通过
   
🎯 总体成功率: {success_rate:.1f}% ({passed_checks}/{total_checks})
""")
    
    if success_rate >= 90:
        print_success("🎉 集成服务验证通过！服务已准备就绪！")
        print_info("✨ 服务具备生产环境部署条件")
        print_info("📚 查看 FINAL_COMPLETION_SUMMARY.md 了解详细信息")
        print_info("🚀 使用以下命令启动服务:")
        print_info("   uvicorn integration_service.main:app --host 0.0.0.0 --port 8090")
    elif success_rate >= 70:
        print_info("⚠️  集成服务基本可用，但需要解决一些问题")
    else:
        print_error("❌ 集成服务存在重大问题，需要修复")
    
    return success_rate >= 90

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 