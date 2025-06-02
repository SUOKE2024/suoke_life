#!/usr/bin/env python3
"""
索克生活高级功能模块测试脚本
测试新增的区块链健康数据管理和AR体质可视化功能
"""

import sys
import json
from pathlib import Path

def test_blockchain_health_data_component():
    """测试区块链健康数据组件"""
    print("🔗 测试区块链健康数据组件...")

    component_path = Path("src/screens/life/components/BlockchainHealthData.tsx")

    if not component_path.exists():
        print("❌ BlockchainHealthData.tsx 组件文件不存在")
        return False

    with open(component_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查关键功能
    required_features = [
        "HealthDataRecord",
        "DataSharingRequest",
        "encryptData",
        "shareData",
        "backupToBlockchain",
        "区块链健康数据",
        "数据加密",
        "安全共享",
        "隐私保护"
    ]

    missing_features = []
    for feature in required_features:
        if feature not in content:
            missing_features.append(feature)

    if missing_features:
        print(f"❌ 缺少功能: {', '.join(missing_features)}")
        return False

    print("✅ 区块链健康数据组件测试通过")
    return True

def test_ar_constitution_visualization_component():
    """测试AR体质可视化组件"""
    print("🥽 测试AR体质可视化组件...")

    component_path = Path("src/screens/life/components/ARConstitutionVisualization.tsx")

    if not component_path.exists():
        print("❌ ARConstitutionVisualization.tsx 组件文件不存在")
        return False

    with open(component_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查关键功能
    required_features = [
        "AcupointData",
        "MeridianData",
        "ConstitutionVisualization",
        "AR体质可视化",
        "经络系统",
        "穴位详解",
        "体质分析",
        "增强现实"
    ]

    missing_features = []
    for feature in required_features:
        if feature not in content:
            missing_features.append(feature)

    if missing_features:
        print(f"❌ 缺少功能: {', '.join(missing_features)}")
        return False

    print("✅ AR体质可视化组件测试通过")
    return True

def test_eco_services_component():
    """测试生态服务组件"""
    print("🌱 测试生态服务组件...")

    component_path = Path("src/screens/suoke/components/EcoServices.tsx")

    if not component_path.exists():
        print("❌ EcoServices.tsx 组件文件不存在")
        return False

    with open(component_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查关键功能
    required_features = [
        "FarmProduct",
        "WellnessDestination",
        "NutritionPlan",
        "食农结合",
        "山水养生",
        "营养配餐",
        "生态社区",
        "有机农产品",
        "自然疗愈"
    ]

    missing_features = []
    for feature in required_features:
        if feature not in content:
            missing_features.append(feature)

    if missing_features:
        print(f"❌ 缺少功能: {', '.join(missing_features)}")
        return False

    print("✅ 生态服务组件测试通过")
    return True

def test_life_screen_integration():
    """测试LIFE频道集成"""
    print("🏠 测试LIFE频道集成...")

    screen_path = Path("src/screens/life/LifeScreen.tsx")

    if not screen_path.exists():
        print("❌ LifeScreen.tsx 文件不存在")
        return False

    with open(screen_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查集成
    required_integrations = [
        "BlockchainHealthData",
        "ARConstitutionVisualization",
        "blockchainModalVisible",
        "arModalVisible",
        "区块链",
        "AR体质"
    ]

    missing_integrations = []
    for integration in required_integrations:
        if integration not in content:
            missing_integrations.append(integration)

    if missing_integrations:
        print(f"❌ 缺少集成: {', '.join(missing_integrations)}")
        return False

    print("✅ LIFE频道集成测试通过")
    return True

def test_suoke_screen_integration():
    """测试SUOKE频道集成"""
    print("🏥 测试SUOKE频道集成...")

    screen_path = Path("src/screens/suoke/SuokeScreen.tsx")

    if not screen_path.exists():
        print("❌ SuokeScreen.tsx 文件不存在")
        return False

    with open(screen_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查集成
    required_integrations = [
        "EcoServices",
        "ecoServicesVisible",
        "生态服务"
    ]

    missing_integrations = []
    for integration in required_integrations:
        if integration not in content:
            missing_integrations.append(integration)

    if missing_integrations:
        print(f"❌ 缺少集成: {', '.join(missing_integrations)}")
        return False

    print("✅ SUOKE频道集成测试通过")
    return True

def test_component_file_structure():
    """测试组件文件结构"""
    print("📁 测试组件文件结构...")

    required_files = [
        "src/screens/life/components/BlockchainHealthData.tsx",
        "src/screens/life/components/ARConstitutionVisualization.tsx",
        "src/screens/suoke/components/EcoServices.tsx"
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ 缺少文件: {', '.join(missing_files)}")
        return False

    print("✅ 组件文件结构测试通过")
    return True

def main():
    """主测试函数"""
    print("🚀 开始测试索克生活高级功能模块...")
    print("=" * 60)

    tests = [
        test_component_file_structure,
        test_blockchain_health_data_component,
        test_ar_constitution_visualization_component,
        test_eco_services_component,
        test_life_screen_integration,
        test_suoke_screen_integration
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            print()

    print("=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有高级功能模块测试通过！")
        print("\n✨ 新增功能总结:")
        print("   • 区块链健康数据管理 - 数据加密、隐私保护、安全共享")
        print("   • AR体质可视化 - 3D人体模型、经络穴位、增强现实")
        print("   • 生态服务体系 - 食农结合、山水养生、营养配餐、生态社区")
        print("   • LIFE频道高级功能集成")
        print("   • SUOKE频道生态服务集成")
        return True
    else:
        print(f"⚠️  有 {total - passed} 个测试失败，请检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)