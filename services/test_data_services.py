#!/usr/bin/env python3
"""
测试数据服务导入问题的脚本
"""

import sys
import os

def test_data_services():
    """测试数据服务的导入"""
    services = [
        'unified-health-data-service',
        'unified-knowledge-service', 
        'communication-service'
    ]
    
    results = {}
    
    for service in services:
        try:
            # 添加服务路径到sys.path
            service_path = os.path.join(os.getcwd(), service)
            if service_path not in sys.path:
                sys.path.insert(0, service_path)
            
            # 尝试导入服务
            if service == 'unified-health-data-service':
                import unified_health_data_service
                results[service] = "✅ 导入成功"
            elif service == 'unified-knowledge-service':
                import unified_knowledge_service
                results[service] = "✅ 导入成功"
            elif service == 'communication-service':
                import communication_service
                results[service] = "✅ 导入成功"
                
        except Exception as e:
            results[service] = f"❌ 导入失败: {str(e)}"
        finally:
            # 清理sys.path
            if service_path in sys.path:
                sys.path.remove(service_path)
    
    # 打印结果
    print("🔍 数据服务导入测试结果:")
    print("=" * 50)
    for service, result in results.items():
        print(f"{service}: {result}")
    
    return results

if __name__ == "__main__":
    test_data_services() 