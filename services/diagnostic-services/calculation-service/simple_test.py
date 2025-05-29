#!/usr/bin/env python3
"""
简化测试脚本

测试算诊微服务的基本功能，避免复杂的模型定义
"""

import sys
import os
from datetime import date

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """测试基本导入"""
    try:
        print("测试基本导入...")
        
        # 测试五运六气数据
        from calculation_service.core.algorithms.wuyun_liuqi.data import (
            TIANGAN, DIZHI, WUYUN_MAPPING, LIUQI_MAPPING
        )
        print("✓ 五运六气数据导入成功")
        
        # 测试计算器
        from calculation_service.core.algorithms.wuyun_liuqi.calculator import WuyunLiuqiCalculator
        print("✓ 五运六气计算器导入成功")
        
        # 测试工具类
        from calculation_service.utils.bazi_calculator import BaziCalculator
        from calculation_service.utils.bagua_calculator import BaguaCalculator
        from calculation_service.utils.ziwu_calculator import ZiwuCalculator
        print("✓ 工具类导入成功")
        
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_wuyun_liuqi():
    """测试五运六气计算"""
    try:
        print("\n测试五运六气计算...")
        
        from calculation_service.core.algorithms.wuyun_liuqi.calculator import WuyunLiuqiCalculator
        
        calculator = WuyunLiuqiCalculator()
        result = calculator.calculate_year_analysis(2024)
        
        print(f"✓ 2024年五运六气分析: {result['year_ganzhi']}")
        print(f"  主运: {result['wuyun']['name']}")
        print(f"  主气: {result['liuqi']['name']}")
        
        return True
    except Exception as e:
        print(f"✗ 五运六气计算失败: {e}")
        return False

def test_bazi_calculation():
    """测试八字计算"""
    try:
        print("\n测试八字计算...")
        
        from calculation_service.utils.bazi_calculator import BaziCalculator
        
        calculator = BaziCalculator()
        result = calculator.calculate_bazi(date(1990, 5, 15), "10:00")
        
        print(f"✓ 八字计算成功:")
        print(f"  年柱: {result['year_ganzhi']}")
        print(f"  月柱: {result['month_ganzhi']}")
        print(f"  日柱: {result['day_ganzhi']}")
        print(f"  时柱: {result['hour_ganzhi']}")
        
        return True
    except Exception as e:
        print(f"✗ 八字计算失败: {e}")
        return False

def test_bagua_calculation():
    """测试八卦计算"""
    try:
        print("\n测试八卦计算...")
        
        from calculation_service.utils.bagua_calculator import BaguaCalculator
        
        calculator = BaguaCalculator()
        result = calculator.calculate_constitution(date(1990, 5, 15), "male")
        
        print(f"✓ 八卦体质分析成功:")
        print(f"  主卦: {result['primary_gua']}")
        print(f"  体质类型: {result['constitution_type']}")
        
        return True
    except Exception as e:
        print(f"✗ 八卦计算失败: {e}")
        return False

def test_ziwu_calculation():
    """测试子午流注计算"""
    try:
        print("\n测试子午流注计算...")
        
        from calculation_service.utils.ziwu_calculator import ZiwuCalculator
        
        calculator = ZiwuCalculator()
        result = calculator.calculate_optimal_time(date.today())
        
        print(f"✓ 子午流注计算成功:")
        print(f"  最佳治疗时间: {result['optimal_hours']}")
        print(f"  经络流注: {result['meridian_flow']}")
        
        return True
    except Exception as e:
        print(f"✗ 子午流注计算失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("算诊微服务简化测试")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_wuyun_liuqi,
        test_bazi_calculation,
        test_bagua_calculation,
        test_ziwu_calculation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    print("=" * 50)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 