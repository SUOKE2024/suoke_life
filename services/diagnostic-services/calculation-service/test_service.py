#!/usr/bin/env python3
"""
算诊微服务测试脚本

用于测试算诊微服务的基本功能
"""

import sys
from pathlib import Path
from datetime import date

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from calculation_service.core.algorithms.wuyun_liuqi import WuyunLiuqiCalculator
from calculation_service.utils.bazi_calculator import BaziCalculator


def test_wuyun_liuqi():
    """测试五运六气计算"""
    print("=== 测试五运六气计算 ===")
    
    calculator = WuyunLiuqiCalculator()
    
    # 测试2024年五运六气
    result = calculator.calculate_wuyun_liuqi(2024)
    
    print(f"年份: {result['year']}")
    print(f"干支: {result['ganzhi']}")
    print(f"五运: {result['wuyun']['type']}")
    print(f"司天: {result['liuqi']['sitian']['type']}")
    print(f"在泉: {result['liuqi']['zaiquan']['type']}")
    print(f"气候影响: {result['climate_influence']}")
    print(f"易发疾病: {', '.join(result['diseases_prone'][:3])}")
    print()


def test_bazi_calculation():
    """测试八字计算"""
    print("=== 测试八字计算 ===")
    
    calculator = BaziCalculator()
    
    # 测试1990年3月15日出生的八字
    birth_date = date(1990, 3, 15)
    birth_time = "14:30"
    
    bazi = calculator.calculate_bazi(birth_date, birth_time)
    
    print(f"出生日期: {birth_date}")
    print(f"出生时间: {birth_time}")
    print(f"年柱: {bazi['year_ganzhi']}")
    print(f"月柱: {bazi['month_ganzhi']}")
    print(f"日柱: {bazi['day_ganzhi']}")
    print(f"时柱: {bazi['hour_ganzhi']}")
    print(f"五行分布: 木{bazi['wuxing']['wood']} 火{bazi['wuxing']['fire']} 土{bazi['wuxing']['earth']} 金{bazi['wuxing']['metal']} 水{bazi['wuxing']['water']}")
    print(f"主导元素: {bazi['wuxing']['dominant_element']}")
    print()
    
    # 测试体质分析
    constitution = calculator.analyze_constitution_from_bazi(bazi)
    print(f"体质类型: {constitution['constitution_type']}")
    print(f"体质特征: {', '.join(constitution['characteristics'][:3])}")
    print(f"健康风险: {', '.join(constitution['health_risks'][:3])}")
    print(f"调养建议: {', '.join(constitution['care_advice'][:3])}")
    print()


def test_year_ganzhi():
    """测试年份干支计算"""
    print("=== 测试年份干支计算 ===")
    
    calculator = WuyunLiuqiCalculator()
    
    test_years = [2020, 2021, 2022, 2023, 2024, 2025]
    
    for year in test_years:
        ganzhi = calculator.get_year_ganzhi(year)
        wuyun = calculator.get_wuyun_from_ganzhi(ganzhi)
        print(f"{year}年: {ganzhi} - {wuyun}")
    
    print()


def main():
    """主测试函数"""
    print("算诊微服务功能测试")
    print("=" * 50)
    
    try:
        test_year_ganzhi()
        test_wuyun_liuqi()
        test_bazi_calculation()
        
        print("✅ 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 