"""
api_test - 索克生活项目模块
"""

from calculation_service.core.algorithms.wuyun_liuqi.calculator import WuyunLiuqiCalculator
from calculation_service.utils.bagua_calculator import BaguaCalculator
from calculation_service.utils.bazi_calculator import BaziCalculator
from calculation_service.utils.ziwu_calculator import ZiwuCalculator
from datetime import date
import json
import os
import sys

#!/usr/bin/env python3
"""
API功能测试脚本

模拟API调用，测试算诊微服务的核心功能
"""


# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_wuyun_api():
    """测试五运六气API"""
    print("\n=== 测试五运六气分析API ===")
    
    try:
        calculator = WuyunLiuqiCalculator()
        result = calculator.calculate_year_analysis(2024)
        
        response = {
            "success": True,
            "data": result,
            "message": "2024年五运六气分析完成"
        }
        
        print("✓ 五运六气API测试成功")
        print(f"  年份干支: {result['year_ganzhi']}")
        print(f"  主运: {result['wuyun']['name']}")
        print(f"  主气: {result['liuqi']['name']}")
        
        return response
        
    except Exception as e:
        print(f"✗ 五运六气API测试失败: {e}")
        return {"success": False, "error": str(e)}

def test_bazi_api():
    """测试八字分析API"""
    print("\n=== 测试八字分析API ===")
    
    try:
        calculator = BaziCalculator()
        birth_date = date(1990, 5, 15)
        birth_time = "10:00"
        
        bazi_result = calculator.calculate_bazi(birth_date, birth_time)
        constitution = calculator.analyze_constitution_from_bazi(bazi_result)
        
        response = {
            "success": True,
            "data": {
                "bazi": bazi_result,
                "constitution": constitution
            },
            "message": "八字分析完成"
        }
        
        print("✓ 八字API测试成功")
        print(f"  年柱: {bazi_result['year_ganzhi']}")
        print(f"  体质类型: {constitution['constitution_type']}")
        
        return response
        
    except Exception as e:
        print(f"✗ 八字API测试失败: {e}")
        return {"success": False, "error": str(e)}

def test_bagua_api():
    """测试八卦分析API"""
    print("\n=== 测试八卦体质分析API ===")
    
    try:
        calculator = BaguaCalculator()
        birth_date = date(1990, 5, 15)
        gender = "male"
        
        result = calculator.calculate_constitution(birth_date, gender)
        
        response = {
            "success": True,
            "data": result,
            "message": "八卦体质分析完成"
        }
        
        print("✓ 八卦API测试成功")
        print(f"  主卦: {result['primary_gua']}")
        print(f"  体质类型: {result['constitution_type']}")
        
        return response
        
    except Exception as e:
        print(f"✗ 八卦API测试失败: {e}")
        return {"success": False, "error": str(e)}

def test_ziwu_api():
    """测试子午流注API"""
    print("\n=== 测试子午流注分析API ===")
    
    try:
        calculator = ZiwuCalculator()
        target_date = date.today()
        
        result = calculator.calculate_optimal_time(target_date)
        
        response = {
            "success": True,
            "data": result,
            "message": "子午流注分析完成"
        }
        
        print("✓ 子午流注API测试成功")
        print(f"  最佳治疗时间: {result['optimal_hours'][:2]}")
        print(f"  当前时辰: {result['current_shichen']['时辰']}")
        
        return response
        
    except Exception as e:
        print(f"✗ 子午流注API测试失败: {e}")
        return {"success": False, "error": str(e)}

def test_comprehensive_api():
    """测试综合分析API"""
    print("\n=== 测试综合算诊分析API ===")
    
    try:
        # 初始化计算器
        wuyun_calculator = WuyunLiuqiCalculator()
        bazi_calculator = BaziCalculator()
        bagua_calculator = BaguaCalculator()
        ziwu_calculator = ZiwuCalculator()
        
        # 参数
        year = 2024
        birth_date = date(1990, 5, 15)
        gender = "male"
        birth_time = "10:00"
        
        # 各项分析
        wuyun_result = wuyun_calculator.calculate_year_analysis(year)
        bazi_result = bazi_calculator.calculate_bazi(birth_date, birth_time)
        bazi_constitution = bazi_calculator.analyze_constitution_from_bazi(bazi_result)
        bagua_result = bagua_calculator.calculate_constitution(birth_date, gender)
        ziwu_result = ziwu_calculator.calculate_optimal_time(birth_date)
        
        response = {
            "success": True,
            "data": {
                "wuyun_liuqi": wuyun_result,
                "bazi": {
                    "calculation": bazi_result,
                    "constitution": bazi_constitution
                },
                "bagua": bagua_result,
                "ziwu": ziwu_result,
                "summary": {
                    "primary_constitution": bazi_constitution["constitution_type"],
                    "bagua_constitution": bagua_result["constitution_type"],
                    "year_influence": wuyun_result["wuyun"]["name"],
                    "optimal_treatment_times": ziwu_result["optimal_hours"][:2]
                }
            },
            "message": "综合算诊分析完成"
        }
        
        print("✓ 综合分析API测试成功")
        print(f"  八字体质: {bazi_constitution['constitution_type']}")
        print(f"  八卦体质: {bagua_result['constitution_type']}")
        print(f"  年运影响: {wuyun_result['wuyun']['name']}")
        print(f"  最佳治疗时间: {ziwu_result['optimal_hours'][:2]}")
        
        return response
        
    except Exception as e:
        print(f"✗ 综合分析API测试失败: {e}")
        return {"success": False, "error": str(e)}

def main():
    """主测试函数"""
    print("=" * 60)
    print("算诊微服务API功能测试")
    print("=" * 60)
    
    # 测试各个API
    tests = [
        ("五运六气分析", test_wuyun_api),
        ("八字分析", test_bazi_api),
        ("八卦体质分析", test_bagua_api),
        ("子午流注分析", test_ziwu_api),
        ("综合算诊分析", test_comprehensive_api),
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if result.get("success", False):
                passed += 1
        except Exception as e:
            print(f"✗ {test_name}测试异常: {e}")
            results[test_name] = {"success": False, "error": str(e)}
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print(f"API测试结果: {passed}/{total} 通过")
    print("=" * 60)
    
    # 保存测试结果到文件
    with open("api_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"详细测试结果已保存到: api_test_results.json")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 