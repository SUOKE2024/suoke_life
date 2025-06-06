"""
test_imports - 索克生活项目模块
"""

        import traceback
import os
import sys

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试相对导入问题
"""


# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_relative_imports():
    """测试相对导入"""
    try:
        # 测试核心模块导入

        print('✅ 核心服务导入成功')

        # 测试接口导入
            IBlindAssistanceService, IVoiceAssistanceService,
            IScreenReadingService, ISignLanguageService
        )

        print('✅ 接口导入成功')

        # 测试装饰器导入

        print('✅ 装饰器导入成功')

        return True

    except ImportError as e:
        print(f'❌ 相对导入失败: {e}')
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_relative_imports()
    exit(0 if result else 1)