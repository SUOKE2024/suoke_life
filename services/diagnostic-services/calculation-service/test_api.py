#!/usr/bin/env python3
"""
算诊服务API测试脚本
索克生活 - 传统中医算诊微服务
"""

import requests

BASE_URL = "http://localhost:8003"


def test_service_info():
    """测试服务信息"""
    print("🔍 测试服务信息...")
    response = requests.get(f"{BASE_URL}/")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"服务: {data['service']}")
        print(f"版本: {data['version']}")
        print(f"功能: {', '.join(data['features'])}")
        print("✅ 服务信息测试通过\n")
    else:
        print("❌ 服务信息测试失败\n")


def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    response = requests.get(f"{BASE_URL}/api/v1/calculation/health")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"服务状态: {data['status']}")
        print(f"算法状态: {data['algorithms']}")
        print("✅ 健康检查测试通过\n")
    else:
        print("❌ 健康检查测试失败\n")


def test_comprehensive_analysis():
    """测试综合算诊分析"""
    print("🔍 测试综合算诊分析...")
    payload = {
        "personal_info": {
            "birth_year": 1990,
            "birth_month": 5,
            "birth_day": 15,
            "birth_hour": 14,
            "gender": "男",
        },
        "analysis_date": "2024-01-15",
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/calculation/comprehensive",
        json=payload,
        headers={"Content-Type": "application/json"},
    )

    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            print("✅ 综合算诊分析测试通过")
            print(f"分析时间: {data['data']['分析时间']}")
            print(f"包含分析: {list(data['data'].keys())}")
            print()
        else:
            print("❌ 综合算诊分析返回失败")
    else:
        print(f"❌ 综合算诊分析测试失败: {response.text}\n")


def test_wuyun_liuqi():
    """测试五运六气分析"""
    print("🔍 测试五运六气分析...")
    response = requests.get(f"{BASE_URL}/api/v1/calculation/wuyun-liuqi/current")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            print("✅ 五运六气分析测试通过")
            print(f"当前运气: {data['data']['当前运气']}")
            print(f"总体特点: {data['data']['总体特点']}")
            print()
        else:
            print("❌ 五运六气分析返回失败")
    else:
        print("❌ 五运六气分析测试失败\n")


def test_cache_stats():
    """测试缓存统计"""
    print("🔍 测试缓存统计...")
    response = requests.get(f"{BASE_URL}/cache/stats")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ 缓存统计测试通过")
        print(f"缓存项数: {data['cache_stats']['total_items']}")
        print(f"最大容量: {data['cache_stats']['max_size']}")
        print(f"使用率: {data['cache_stats']['usage_ratio']:.1%}")
        print()
    else:
        print("❌ 缓存统计测试失败\n")


def main():
    """主测试函数"""
    print("🚀 开始测试索克生活算诊服务API")
    print("=" * 50)

    try:
        test_service_info()
        test_health_check()
        test_comprehensive_analysis()
        test_wuyun_liuqi()
        test_cache_stats()

        print("🎉 所有测试完成！")
        print("=" * 50)

    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保服务正在运行在 http://localhost:8003")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")


if __name__ == "__main__":
    main()
