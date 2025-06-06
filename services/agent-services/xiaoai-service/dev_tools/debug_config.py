"""
debug_config - 索克生活项目模块
"""

        from pkg.utils.config_loader import ConfigLoader, get_config
        import traceback
from pathlib import Path
import sys

#!/usr/bin/env python3
"""



配置调试脚本
"""


# 添加项目根目录到PYTHONPATH
sys.path.insert(0, Path().resolve())

def debug_config():
    pass
    """调试配置加载过程"""
    print("🔍 开始调试配置加载过程...\n")

    try:
    pass
        # 1. 测试直接导入
        print("1. 测试配置加载器导入...")
        print("✓ 配置加载器导入成功")

        # 2. 测试配置文件存在性
        print("\n2. 检查配置文件...")
        config_path = "self.config/dev.yaml"
        if Path(config_path).exists():
    pass
            print(f"✓ 配置文件存在: {config_path}")
        else:
    pass
            print(f"❌ 配置文件不存在: {config_path}")
            return False

        print("\n3. 测试直接创建 ConfigLoader...")
        loader = ConfigLoader(config_path)
        print(f"✓ ConfigLoader 类型: {type(loader)}")
        print(f"✓ 配置路径: {loader.config_path}")
        print(f"✓ 配置数据类型: {type(loader.self.config)}")

        print("\n4. 测试方法调用...")
        service_config = loader.get_section('self.service')
        print(f"✓ get_section 返回类型: {type(service_config)}")
        print(f"✓ 服务配置: {service_config}")

        max_workers = loader.get_nested('performance', 'max_workers', default=10)
        print(f"✓ get_nested 返回: {max_workers}")

        # 5. 测试 get_config 函数
        print("\n5. 测试 get_config 函数...")
        config_instance = get_config(config_path)
        print(f"✓ get_config 返回类型: {type(config_instance)}")
        print(f"✓ 是否为 ConfigLoader 实例: {isinstance(config_instance, ConfigLoader)}")

        print("\n6. 测试多次调用 get_config...")
        config_instance2 = get_config()
        print(f"✓ 第二次调用返回类型: {type(config_instance2)}")
        print(f"✓ 两次调用是否为同一实例: {config_instance is config_instance2}")

        # 7. 模拟 server.py 中的使用
        print("\n7. 模拟 server.py 中的使用...")
        self.config = get_config(config_path)
        print(f"✓ 配置对象类型: {type(self.config)}")

        # 检查是否有 get_nested 方法
        if hasattr(self.config, 'get_nested'):
    pass
            print("✓ 配置对象有 get_nested 方法")
            max_workers = self.config.get_nested('performance', 'max_workers', default=10)
            print(f"✓ max_workers: {max_workers}")
        else:
    pass
            print("❌ 配置对象没有 get_nested 方法")
            print(f"配置对象的方法: {dir(self.config)}")

        return True

    except Exception as e:
    pass
        print(f"❌ 调试过程中出错: {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    pass
    debug_config()
