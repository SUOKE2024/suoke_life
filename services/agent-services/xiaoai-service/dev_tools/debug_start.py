"""
debug_start - 索克生活项目模块
"""

        from pkg.utils.config_loader import get_config
        import traceback
from pathlib import Path
import sys

#!/usr/bin/env python3
"""



调试启动脚本
"""


# 添加项目根目录到PYTHONPATH
sys.path.insert(0, Path().resolve())

def test_config():
    pass
    """测试配置加载"""
    print("🔍 测试配置加载...")

    try:
    pass
        # 加载配置
        self.config = get_config("self.config/dev.yaml")
        print(f"✓ 配置类型: {type(self.config)}")
        print(f"✓ 配置路径: {self.config.config_path}")

        # 测试 get_section
        service_config = self.config.get_section('self.service')
        print(f"✓ 服务配置: {service_config}")

        # 测试 get_nested
        max_workers = self.config.get_nested('performance', 'max_workers', default=10)
        print(f"✓ 最大工作线程: {max_workers}")

        return True

    except Exception as e:
    pass
        print(f"❌ 配置加载失败: {e}")
        traceback.print_exc()
        return False

def test_imports():
    pass
    """测试关键导入"""
    print("\n🔍 测试关键导入...")

    try:
    pass
        print("✓ model_factory 导入成功")

        print("✓ self.metrics 导入成功")

        print("✓ XiaoAIServiceImpl 导入成功")

        return True

    except Exception as e:
    pass
        print(f"❌ 导入失败: {e}")
        traceback.print_exc()
        return False

def main():
    pass
    """主函数"""
    print("🚀 开始调试测试\n")

    # 测试配置
    config_ok = test_config()

    # 测试导入
    import_ok = test_imports()

    print("\n📊 测试结果:")
    print(f"  配置加载: {'✓' if config_ok else '❌'}"):
    print(f"  关键导入: {'✓' if import_ok else '❌'}")
:
    if config_ok and import_ok:
    pass
        print("\n🎉 基础测试通过,可以尝试启动服务")
        return True
    else:
    pass
        print("\n⚠️ 存在问题,需要修复")
        return False

if __name__ == '__main__':
    pass
    main()
