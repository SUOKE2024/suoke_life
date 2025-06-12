#!/usr/bin/env python3
"""
测试所有微服务的基本功能
"""

import sys
import os
from pathlib import Path

def test_service_imports():
    """测试各服务的基本导入功能"""
    
    results = {}
    
    # 测试xiaoai-service
    try:
        sys.path.insert(0, "agent-services/xiaoai-service")
        from xiaoai.core.agent import XiaoAiAgent
        results["xiaoai-service"] = "✅ 导入成功"
    except Exception as e:
        results["xiaoai-service"] = f"❌ 导入失败: {str(e)[:50]}"
    
    # 测试blockchain-service
    try:
        sys.path.insert(0, "blockchain-service")
        from suoke_blockchain_service.exceptions import BlockchainServiceError
        results["blockchain-service"] = "✅ 导入成功"
    except Exception as e:
        results["blockchain-service"] = f"❌ 导入失败: {str(e)[:50]}"
    
    # 测试api-gateway
    try:
        sys.path.insert(0, "api-gateway")
        from suoke_api_gateway.core.gateway import APIGateway
        results["api-gateway"] = "✅ 导入成功"
    except Exception as e:
        results["api-gateway"] = f"❌ 导入失败: {str(e)[:50]}"
    
    # 测试user-management-service
    try:
        sys.path.insert(0, "user-management-service")
        from user_management_service.models import User
        results["user-management-service"] = "✅ 导入成功"
    except Exception as e:
        results["user-management-service"] = f"❌ 导入失败: {str(e)[:50]}"
    
    return results

def check_service_syntax():
    """检查各服务的语法错误数量"""
    
    services = [
        "agent-services/xiaoai-service",
        "blockchain-service", 
        "communication-service",
        "utility-services",
        "api-gateway",
        "user-management-service"
    ]
    
    syntax_results = {}
    
    for service in services:
        if os.path.exists(service):
            try:
                # 使用ruff检查语法错误
                import subprocess
                result = subprocess.run(
                    ["ruff", "check", service], 
                    capture_output=True, 
                    text=True,
                    cwd="."
                )
                error_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                syntax_results[service] = error_count
            except Exception as e:
                syntax_results[service] = f"检查失败: {e}"
        else:
            syntax_results[service] = "目录不存在"
    
    return syntax_results

def main():
    """主测试函数"""
    
    print("🔍 索克生活微服务优化验证报告")
    print("=" * 50)
    
    # 测试导入功能
    print("\n📦 服务导入测试:")
    import_results = test_service_imports()
    for service, result in import_results.items():
        print(f"  {service}: {result}")
    
    # 检查语法错误
    print("\n🔧 语法错误统计:")
    syntax_results = check_service_syntax()
    total_errors = 0
    for service, errors in syntax_results.items():
        if isinstance(errors, int):
            total_errors+=errors
            status = "✅" if errors==0 else "🔄" if errors < 1000 else "⚠️"
            print(f"  {service}: {status} {errors} 个错误")
        else:
            print(f"  {service}: ❌ {errors}")
    
    # 计算成功率
    successful_imports = sum(1 for result in import_results.values() if "✅" in result)
    import_success_rate = (successful_imports / len(import_results)) * 100
    
    print(f"\n📊 优化成果总结:")
    print(f"  导入成功率: {import_success_rate:.1f}%")
    print(f"  总语法错误: {total_errors}")
    
    if import_success_rate>=75 and total_errors < 15000:
        print(f"\n🎉 优化效果良好！系统基本可用。")
    elif import_success_rate>=50:
        print(f"\n👍 优化有显著进展，继续努力！")
    else:
        print(f"\n⚠️ 需要进一步优化。")

if __name__=="__main__":
    main() 