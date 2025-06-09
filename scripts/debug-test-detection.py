#!/usr/bin/env python3
"""
调试测试文件检测逻辑
"""

from pathlib import Path

def debug_test_detection():
    """调试测试文件检测"""
    service_path = Path('services/unified-health-data-service')
    tests_path = service_path / 'tests'
    
    print("🔍 调试测试文件检测...")
    print(f"测试路径: {tests_path}")
    print(f"路径存在: {tests_path.exists()}")
    
    if tests_path.exists():
        print("\n📁 找到的测试文件:")
        for test_file in tests_path.rglob('test_*.py'):
            file_path_str = str(test_file)
            file_name = test_file.name
            
            print(f"  文件: {test_file}")
            print(f"    文件名: {file_name}")
            print(f"    路径字符串: {file_path_str}")
            
            # 检测逻辑
            is_health_data = 'health_data' in file_path_str or 'health-data' in file_path_str
            is_database = 'database' in file_name or 'db' in file_name
            is_integration = 'integration' in file_path_str
            is_unit = 'unit' in file_path_str
            
            print(f"    健康数据测试: {is_health_data}")
            print(f"    数据库测试: {is_database}")
            print(f"    集成测试: {is_integration}")
            print(f"    单元测试: {is_unit}")
            print()

if __name__ == "__main__":
    debug_test_detection() 