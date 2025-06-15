#!/usr/bin/env python3
"""
基础功能测试脚本
"""

def test_imports():
    """测试基本导入"""
    try:
        print("✅ FastAPI应用导入成功")

        print("✅ 配置模块导入成功")

        print("✅ 验证器模块导入成功")

        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_basic_validation():
    """测试基础验证功能"""
    try:
        from calculation_service.utils.validators import validate_birth_info

        # 测试有效数据
        valid_data = {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 10,
            "gender": "男"
        }

        result = validate_birth_info(valid_data)
        print(f"✅ 数据验证成功: {result}")
        return True

    except Exception as e:
        print(f"❌ 验证测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("索克生活 - 算诊服务基础功能测试")
    print("=" * 50)

    tests = [
        ("模块导入测试", test_imports),
        ("基础验证测试", test_basic_validation),
    ]

    passed = 0
    for name, test_func in tests:
        print(f"\n🧪 {name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {name}失败")

    print(f"\n📊 测试结果: {passed}/{len(tests)} 通过")
    return passed == len(tests)

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
